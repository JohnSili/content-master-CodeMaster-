from typing import Dict, Optional
import asyncio
from openai import OpenAI

class TextGenerator:
    def __init__(self):
        self.client = OpenAI(
            # base_url="https://openrouter.ai/api/v1",
            # api_key='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'
            api_key="glhf_ee6fa9ada3293f788dfd336a31971a84",
            base_url="https://glhf.chat/api/openai/v1"
        )

    async def generate_article(self, topic: str, length: int, style: str, author_profile: Optional[Dict] = None, model: str = "reflection_llama_3.1_70b") -> str:
        prompt = self._create_prompt(topic, length, style, author_profile)
        
        try:
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional writer creating well-structured, logical articles with clear paragraph divisions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=length * 4  # Примерное соотношение токенов к словам
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating article: {str(e)}")
            return f"Error generating article about {topic}. Please try again later."

    def _create_prompt(self, topic: str, length: int, style: str, author_profile: Optional[Dict] = None) -> str:
        prompt = f"Write an article about {topic}. "
        prompt += f"The article should be approximately {length} words long and written in a {style} style. "
        prompt += "Structure the article with a clear introduction, body paragraphs, and conclusion. "
        prompt += "Use logical transitions between paragraphs and ideas. "
        
        if author_profile:
            prompt += f"Write in the style of {author_profile['name']}. "
            prompt += f"Consider their specialty in {author_profile['specialty']}. "
            prompt += f"Use phrases like: {author_profile['phrases']}. "
            prompt += f"The overall tone should be {author_profile['text_tone']}. "
        
        prompt += "Begin each paragraph with a topic sentence and develop the idea within the paragraph. "
        prompt += "Ensure that the article flows logically from one point to the next. "
        prompt += "End with a strong conclusion that summarizes the main points."

        return prompt

    def get_available_models(self):
        return [
            # "hf:deepseek-ai/deepseek-llm-67b-chat",
            # "hf:google/gemma-2-27b-it",
            # "hf:google/gemma-2-9b-it",
            # "hf:google/gemma-2b-it",
            "hf:meta-llama/Meta-Llama-3.1-405B-Instruct",
            "hf:meta-llama/Meta-Llama-3-8B-Instruct",
            "hf:meta-llama/Meta-Llama-3.1-70B-Instruct",
            "hf:meta-llama/Meta-Llama-3.1-8B-Instruct",
            "hf:mistralai/Mistral-7B-Instruct-v0.3",
            # "hf:Qwen/Qwen1.5-110B-Chat",
            # "hf:Qwen/Qwen1.5-14B-Chat",
            # "hf:Qwen/Qwen1.5-72B-Chat"
        ]

text_generator = TextGenerator()