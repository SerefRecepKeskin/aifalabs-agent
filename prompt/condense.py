# Define a better prompt template for query condensing
CONDENSE_PROMPT_TEMPLATE = """You are an AI assistant managing queries across multiple domains such as cities/weather, research, and products.
Your task is to read a conversation between a user and an assistant, and rephrase the user's question into a standalone question that captures all relevant context from the conversation history.
Additionally, ensure the question is clear enough to determine the appropriate domain-specific agent (e.g., weather, research, products) to handle the query.

Chat History:
{chat_history}

User Question: {question}

Standalone Question:"""