import chainlit as cl

async def list_of_starter() -> list[cl.Starter]:
    """
    Returns a list of starter options for the chatbot interface.
    Each starter contains a label, message prompt, and associated icon.

    Returns:
        list[cl.Starter]: A list of predefined starter options.
    """
    return [
        cl.Starter(
            label="Learn machine learning",
            message="Recommend some resources to learn about machine learning",
            icon="/public/starters/human-learn.svg",
        ),
        cl.Starter(
            label="Search a web page",
            message="Summarize this LangChain documentation page in 3 lines https://python.langchain.com/docs/tutorials/summarization/",
            icon="/public/starters/search-globe.svg",
        ),
        cl.Starter(
            label="Write some code",
            message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up",
            icon="/public/starters/python.svg",
        ),
    ]