import chainlit as cl

async def command_list() -> list:
    """Returns a list of available commands with their details."""
    return [
        {
            "id": "Search", 
            "icon": "globe", 
            "description": "Find information on the web"
        },
        {
            "id": "Chat", 
            "icon": "message-square-text", 
            "description": "Chat with the agent"
        },
        {
            "id": "Summary", 
            "icon": "pen-tool", 
            "description": "Summarize provided content"
        },
    ]