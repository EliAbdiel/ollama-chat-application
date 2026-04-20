import chainlit as cl
from .chat_starters import list_of_starter

async def list_of_profiles(current_user:cl.User) -> list[cl.ChatProfile]:
    """
    Returns a list of available chat profiles.
    Each chat profile represents a different LLM model configuration.
    
    Returns:
        list[cl.ChatProfile]: A list of chat profiles.
    """
    if not current_user.identifier:
        return None

    return [
        cl.ChatProfile(
            name="gemma4:31b-cloud",
            markdown_description="The underlying LLM model is **Gemma4**.",
            icon="public/model/gemma.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="gpt-oss:120b-cloud",
            markdown_description="The underlying LLM model is **GPT-OSS**.",
            icon="public/model/openai.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="deepseek-v3.2:cloud",
            markdown_description="The underlying LLM model is **DeepSeek-V3.2**.",
            icon="public/model/deepseek.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="qwen3.5:397b-cloud",
            markdown_description="The underlying LLM model is **Qwen3.5**.",
            icon="public/model/qwen.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="kimi-k2.5:cloud",
            markdown_description="The underlying LLM model is **Kimi-K2.5**.",
            icon="public/model/kimi.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="glm-5.1:cloud",
            markdown_description="The underlying LLM model is **Glm-5.1**.",
            icon="public/model/zai.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="minimax-m2.7:cloud",
            markdown_description="The underlying LLM model is **Minimax-m2.7**.",
            icon="public/model/minimax.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="mistral-large-3:675b-cloud",
            markdown_description="The underlying LLM model is **Mistral-Large-3**.",
            icon="public/model/mistral.svg",
            starters=await list_of_starter(),
        ),
    ]