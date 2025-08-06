import httpx
from app.config import settings

class OpenAIClient:
    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not found in settings")
        
        self.base_url = "https://api.openai.com/v1"
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def create_chat_completion(self, model: str, messages: list, temperature: float = 0.7, max_tokens: int = 1500):
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        response = await self.client.post(f"{self.base_url}/chat/completions", json=data)
        response.raise_for_status()
        return response.json()

openai_client = OpenAIClient()
