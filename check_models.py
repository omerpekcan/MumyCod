from google import genai
import os
from dotenv import load_dotenv

# .env dosyasındaki anahtarı okur
load_dotenv()
api_key = os.getenv("AIzaSyCQp9FyhP8GLyMe6hUaeKAdgW7Mqx81aNw") 

client = genai.Client(api_key=api_key)

print("--- Kullanılabilir Modeller ---")
for m in client.models.list():
    print(f"Model: {m.name}")
    print(f"Açıklama: {m.description}")
    print("-" * 30)