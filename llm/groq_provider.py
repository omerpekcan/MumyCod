from groq import Groq
from llm.base_provider import BaseProvider


class GroqProvider(BaseProvider):

    def __init__(
        self,
        api_key: str,
        model_name: str = "llama-3.3-70b-versatile"
    ):
        super().__init__(api_key, model_name)

        self.client = Groq(
            api_key=self.api_key
        )

    def generate(self, prompt: str) -> str:

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return completion.choices[0].message.content

    def chat(self, messages: list) -> str:

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )

        return completion.choices[0].message.content

    def summarize(self, text: str) -> str:

        return self.generate(
            f"Özetle:\n\n{text}"
        )

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "Embedding henüz eklenmedi."
        )