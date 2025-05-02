from typing import List, Dict, Any, Optional
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import QueryBundle
from llama_index.core.indices.prompt_helper import PromptHelper
from llama_index.core.prompts import PromptTemplate
from llama_index.core import Settings
from prompt.condense import CONDENSE_PROMPT_TEMPLATE


class ImprovedCondenseQueryEngine:
    """Advanced query condensing engine for better context handling."""
    
    def __init__(self, llm=None):
        self.llm = llm or Settings.llm
        self.condense_template = PromptTemplate(CONDENSE_PROMPT_TEMPLATE)
    
    async def condense_question(self, question: str, chat_history: List[Dict[str, str]]) -> str:
        """Condense a question based on chat history."""
        if not chat_history:
            return question
            
        # Format chat history for the prompt
        formatted_history = ""
        for entry in chat_history:
            if "user_message" in entry:
                formatted_history += f"User: {entry['user_message']}\n"
            if "assistant_message" in entry:
                formatted_history += f"Assistant: {entry['assistant_message']}\n"
        
        # Format the prompt
        prompt = self.condense_template.format(
            chat_history=formatted_history,
            question=question
        )
        
        # Get condensed question from LLM
        response = await self.llm.acomplete(prompt)
        condensed_question = response.text.strip()
        
        # Log for debugging
        print(f"Original question: {question}")
        print(f"Condensed question: {condensed_question}")
        
        return condensed_question

    async def condense_with_additional_context(self, 
                                        question: str, 
                                        chat_history: List[Dict[str, str]], 
                                        additional_context: Optional[str] = None) -> str:
        """Condense a question with optional additional context."""
        condensed_question = await self.condense_question(question, chat_history)
        
        if additional_context:
            # Integrate additional context if provided
            enhanced_question = f"""
            Based on the condensed question: "{condensed_question}"
            And considering this additional context: {additional_context}
            Provide a comprehensive response.
            """
            return enhanced_question
        
        return condensed_question
