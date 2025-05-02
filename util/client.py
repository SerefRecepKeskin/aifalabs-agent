from typing import Optional

from llama_index.llms.gemini import Gemini
from .logger import logger
from config import config


class GeminiClient(Gemini):
    def __init__(
        self,
        model: Optional[str] = None,
    ):
        model_name = model or config.gemini.model
        # Gemini API requires model names to be prefixed with "models/"
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
            
        super().__init__(
            model=model_name,
            api_key=config.gemini.api_key,
            generation_config={
                "max_output_tokens": config.gemini.max_tokens,
                "candidate_count": 1,
               # "response_mime_type":"application/json"
            }
        )
        logger.info('Initialized Gemini with model %s', self.model)
