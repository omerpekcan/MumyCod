from dotenv import load_dotenv
from llm.groq_provider import GroqProvider
import os

load_dotenv()

print("API KEY:", os.getenv("GROQ_API_KEY"))

provider = GroqProvider(
    api_key=os.getenv("GROQ_API_KEY")
)

print(
    provider.generate("Merhaba")
)