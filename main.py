import json
import chainlit as cl
from mcp import ClientSession
from typing import Dict, Optional
from chainlit.types import ThreadDict
from src.log.logger import setup_logger
from src.ui.chat_resume import resume_chats
from src.ui.chat_profiles import list_of_profiles
from src.llm.call_model import call_ollama, model_name
from src.document.document_processor import DocumentProcessor
from src.database.persistent_data_layer import init_data_layer
from src.llm.speech_to_text import audio_chunk, audio_transcription

logger = setup_logger('MAIN PROCESSOR')

@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  """Callback function for OAuth authentication."""
  return default_user

@cl.step(type="tool") 
async def call_tool(tool_name: str, tool_args: dict):
    """
    Executes a remote MCP tool by name with the provided arguments.

    This function:
    1. Locates the MCP connection that exposes the requested tool.
    2. Retrieves the active session for that connection.
    3. Invokes the tool and returns its JSON-serialized result.
    
    If the tool or session is unavailable, an error object is returned instead.
    """
    current_step = cl.context.current_step
    current_step.name = tool_name

    # Identify which mcp is used
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_name = None

    for connection_name, tools in mcp_tools.items():
        if any(tool['function']['name'] == tool_name for tool in tools):
            mcp_name = connection_name
            break
    
    if not mcp_name:
        current_step.output = json.dumps({"error": f"Tool {tool_name} not found in any MCP connection"})
        return current_step.output
    
    try:
        mcp_sessions = getattr(cl.context.session, 'mcp_sessions', {})
        if mcp_name in mcp_sessions:
            mcp_session = mcp_sessions[mcp_name][0]  # First element is the session
            current_step.output = await mcp_session.call_tool(tool_name, tool_args)
        else:
            current_step.output = json.dumps({"error": f"MCP session {mcp_name} not available"})
    except Exception as e:
        current_step.output = json.dumps({"error": str(e)})
    
    return current_step.output

@cl.set_chat_profiles
async def chat_profile(current_user:cl.User):
    """
    Sets up the available chat profiles for the application. 
    Each profile corresponds to a different LLM model configuration.
    
    Returns:
        ChatProfile
            The chat profile (LLM) selected by the user.
    """
    return await list_of_profiles(current_user)

@cl.on_chat_start
async def on_chat_start() -> None:
    """Initializes user session variables at the start of a chat."""
    cl.user_session.set("chat_history", [])
    cl.user_session.set("mcp_tools", {})
    cl.user_session.set("audio_buffer", None)

    user = cl.user_session.get("user")
    user.metadata["chat_profile"] = cl.user_session.get("chat_profile")

    logger.info(f"{user.identifier} has started the conversation with profile: {user.metadata['chat_profile']}")

@cl.on_mcp_connect
async def on_mcp(connection, session: ClientSession):
    """
    Triggered when a new MCP (Model-Context-Protocol) connection is established.

    Discovers and registers all available tools exposed by the remote MCP server,
    storing their metadata in the user session so they can be invoked later
    during chat interactions.
    """
    result = await session.list_tools()
    
    # Process tool metadata
    tools = [{
    "type": "function",
    "function": {
        "name": t.name,
        "description": t.description,
        "parameters": t.inputSchema,
    }} for t in result.tools]
    
    # Store tools for later use
    mcp_tools = cl.user_session.get("mcp_tools", {})
    mcp_tools[connection.name] = tools
    logger.info(f"Connected MCP: {mcp_tools}")
    cl.user_session.set("mcp_tools", mcp_tools)

@cl.on_audio_start
async def on_audio_start():
    """Handles the start of audio input from the user."""
    cl.user_session.set("audio_chunks", [])
    return True

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk) -> None:
    """
    Handles incoming audio chunks during user input.

    Receives audio chunks, stores the audio data in a buffer, and 
    updates the session with the buffer.

    Parameters:
    ----------
    audio_chunk : InputAudioChunk
        The audio chunk to process.
    """
    await audio_chunk(chunk=chunk)

@cl.on_audio_end
async def on_audio_end() -> None:
    """
    Processes the voice message and analyzes user intent.

    Converts the audio to text using the selected chat profile. 
    Handles document analysis (file attachments) and determines 
    user intent for chatbot functionalities. Returns text and 
    voice responses depending on attached file types and user intents.
    """
    try:
        transcription = await audio_transcription()
        # Process transcription
        user_message = cl.Message(
            content=transcription,
            author="User",
            type="user_message"
        )
        
        await user_message.send()
        await on_message(user_message)
        return True
    except Exception as e:
        logger.error(f"Error processing audio end: {e}")
        await cl.Message(content=f"Audio processing error. Please try again.").send()

@cl.on_message
async def on_message(user_message: cl.Message) -> None:
    """
    Processes text messages, file attachments, and user intent.

    Handles text input, detects files in the user's message, 
    and processes them. It also interacts with the LLM chat profile 
    to respond based on the attached files and user intent for 
    chatbot functionalities.

    Args:
    ----------
    user_message : Message
        The incoming message with potential file attachments.
    """
    if not user_message or not user_message.content:
        logger.error("Received invalid or None message")
        return
    
    if user_message.elements:
        logger.info("Processing user message with attached files")
        
        docs = [
            f
            for f in user_message.elements
            if str(f.name).lower().endswith((".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"))
        ]

        file = docs[0] if docs else None

        if not file or file is None:
            logger.warning("No valid document files found")
            raise ValueError("No valid document files found")
        
        logger.info(f"Found document file: {str(file.name)}, mime: {str(file.mime)}")

        # Process the document
        processor = DocumentProcessor()    
        extracted_content = await processor.process_single_file_async(file=file)
        
        if extracted_content:
            user_message.content += f"\n\n{extracted_content}"
            logger.info("Appended extracted content to user message")
    
    user = cl.user_session.get("user")
    chat_profile = user.metadata["chat_profile"]
    logger.info(f"Selected chat profile: {chat_profile}")

    model = await model_name(profile=str(chat_profile))

    if not model:
        logger.error(f"Could not determine model for chat profile: {chat_profile}")
        return
    
    logger.info(f"Using model: {model}")

    chat_history = cl.user_session.get("chat_history", [])
    
    chat_history.append({"role": "user", "content": user_message.content})
    logger.info(f"Chat history before call llm: {chat_history}")

    try:

        response = await call_ollama(model=model, messages=chat_history)
        
        if response:
            chat_history.append({"role": "assistant", "content": response})
            logger.info(f"Chat history after call llm: {chat_history}")
            cl.user_session.set("chat_history", chat_history)
            await cl.Message(content=response).send()

        else:
            logger.warning("Empty response from Ollama")
            await cl.Message(content="I apologize, but I couldn't generate a response. Please try again.").send()
    
    except Exception as e:
        logger.error(f"Unexpected error in on_message: {e}")
        await cl.Message(content="An unexpected error occurred. Please try again.").send()

@cl.data_layer
def data_layer():
    """Initializes the SQLAlchemy data layer for Chainlit."""
    return init_data_layer()

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict) -> None:
    """
    Resumes archived chat conversations.

    Retrieves previous chat threads to load them into memory and 
    enables users to continue a conversation.

    Args:
    ----------
    thread : ThreadDict
        A dictionary containing the thread's information and messages.
    """
    await resume_chats(thread=thread)
