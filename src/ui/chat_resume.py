import chainlit as cl
from chainlit.types import ThreadDict

async def resume_chats(thread: ThreadDict) -> None:
    """
    Retrieves previous chat threads to load them into memory and 
    enables users to continue a conversation.

    Args:
    ----------
    thread : ThreadDict
        A dictionary containing the thread's information and messages.
    """
    cl.user_session.set("chat_history", [])

    for message in thread["steps"]:
        if message["type"] == "user_message":
            cl.user_session.get("chat_history").append(
                {"role": "user", "content": message["output"]}
            )
        elif message["type"] == "assistant_message":
            cl.user_session.get("chat_history").append(
                {"role": "assistant", "content": message["output"]}
            )