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
            name="gpt-oss:120b-cloud",
            markdown_description="The underlying LLM model is **GPT-OSS**.",
            icon="public/model/openai.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="deepseek-v3.1:671b-cloud",
            markdown_description="The underlying LLM model is **DeepSeek-V3.1**.",
            icon="public/model/deepseek.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="qwen3-vl:235b-cloud",
            markdown_description="The underlying LLM model is **Qwen3-vl**.",
            icon="public/model/qwen.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="kimi-k2:1t-cloud",
            markdown_description="The underlying LLM model is **Kimi-K2**.",
            icon="public/model/kimi.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="glm-4.6:cloud",
            markdown_description="The underlying LLM model is **Glm-4.6**.",
            icon="public/model/zai.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="minimax-m2:cloud",
            markdown_description="The underlying LLM model is **Minimax-m2**.",
            icon="public/model/minimax.svg",
            starters=await list_of_starter(),
        ),
        cl.ChatProfile(
            name="gemini-3-pro-preview",
            markdown_description="The underlying LLM model is **Gemini 3 Pro**.",
            icon="public/model/gemini.svg",
            starters=await list_of_starter(),
        ),
    ]