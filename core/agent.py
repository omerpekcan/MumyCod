import re
import os
import traceback
from llm.gemini_provider import GeminiProvider
from tools.file_tools import read_file, write_to_file
from tools.terminal_tools import execute_command
from retrieval.retriever import CodeRetriever

class MumyCodAgent:
    def __init__(self):
        self.provider = GeminiProvider()
        self.retriever = CodeRetriever()
        self.history = []

    def ask(self, user_query: str) -> str:
        print(f"[DEBUG] Soru alındı: {user_query}")
        try:
            # 1. LLM'e sor
            print("[DEBUG] LLM'e gönderiliyor...")
            response = self.provider.chat(user_query)
            
            # Nesne kontrolü
            text = response.text if hasattr(response, "text") else str(response)
            print(f"[DEBUG] LLM Yanıtı: {text[:50]}...")
            
            # 2. Araçları parse et
            tool_match = re.search(r"\[TOOL:(\w+)\((.*?)\)\]", text)
            if tool_match:
                tool_name, tool_args = tool_match.groups()
                print(f"[DEBUG] Araç tespit edildi: {tool_name}")
                
                # Basit araç switch-case
                if tool_name == "read_file":
                    res = read_file(tool_args)
                elif tool_name == "execute_command":
                    res = execute_command(tool_args)
                else:
                    res = "Bilinmeyen araç."
                
                print(f"[DEBUG] Araç sonucu: {res[:50]}...")
                return res
            
            return text
            
        except Exception as e:
            print("[DEBUG] HATA YAKALANDI!")
            traceback.print_exc()
            return f"HATA: {str(e)}"