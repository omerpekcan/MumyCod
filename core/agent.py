import re
import os
import json
import traceback
from llm.provider_manager import ProviderManager
from tools.file_tools import read_file, write_file
from tools.terminal_tools import execute_command
from tools.git_tools import GitTools
from retrieval.retriever import CodeRetriever

class MumyCodAgent:
    COMMAND_MAP = {
        '/çıkış': 'exit',
        '/sağlayıcı': 'provider',
        '/model': 'model',
        '/temizle': 'clear',
        '/durum': 'status'
    }

    def __init__(self):
        print("MumyCod Terminal Başlatıldı")
        # ProviderManager ile çoklu sağlayıcı desteği aktif
        self.provider_manager = ProviderManager()
        # brain.json dosyasının doğru yolda olduğundan emin oluyoruz
        self.retriever = CodeRetriever(brain_path="memory/brain.json")
        self.git_tools = GitTools()
        self.history = []
        
        # Yapay zekaya nasıl davranması gerektiğini dikte eden sistem talimatı
        self.system_prompt = (
            "Sen bir ToolExecutionEngine'sin. Görevin kullanıcıyla sohbet etmek veya açıklama yapmak değil, SADECE araçları tetiklemektir.\n\n"
            "KESİN KURALLAR:\n"
            "1. Yanıtın SADECE ve HER ZAMAN [TOOL_JSON]{...}[/TOOL_JSON] formatında olmalıdır ve içindeki JSON valid olmalıdır.\n"
            "2. Başında veya sonunda hiçbir ek metin, açıklama, 'Tabii', 'İşte kod:' gibi ifadeler OLMAYACAKTIR.\n"
            "3. Kullanıcıya talimat verme, işlemi bizzat yap.\n"
            "4. Tek seferde sadece bir adet [TOOL_JSON] çağrısı yap.\n"
            "5. content alanı dahil TÜM string değerlerdeki özel karakterler (\\n, ', \", [, ], vb.) JSON string olarak otomatik escape edilmelidir.\n\n"
            "KULLANILABİLİR ARAÇLAR:\n"
            "- write_file(filepath, content)\n"
            "- read_file(filepath)\n"
            "- execute_command(command)\n"
            "- search_codebase(query)\n"
            "- git_commit(message)\n"
            "- git_push()\n\n"
            "ÖRNEK YANITLAR:\n"
            "[TOOL_JSON]{\"tool\": \"write_file\", \"args\": {\"filepath\": \"test.py\", \"content\": \"print(\\\"merhaba\\\")\"}}[/TOOL_JSON]\n"
            "[TOOL_JSON]{\"tool\": \"read_file\", \"args\": {\"filepath\": \"main.py\"}}[/TOOL_JSON]"
        )
        print("[DEBUG] MumyCodAgent başarıyla başlatıldı.")

    def handle_command(self, user_query: str) -> str:
        """Komutları işler ve eşleşen komut varsa çalıştırır."""
        if user_query.startswith('/'):
            cmd = self.COMMAND_MAP.get(user_query.split()[0])
            if cmd:
                return f"Komut işleniyor: {cmd}"
            return "Bilinmeyen komut"
        return ""

    def _detect_error_in_result(self, result: str) -> tuple[bool, str]:
        """Araç çıktısında hata var mı kontrol eder."""
        error_keywords = [
            r'hata', r'error', r'false', r'başarısız', 
            r'failed', r'bulunamadı', r'not found', r'exception',
            r'traceback', r'errno', r'invalid path', r'yolu yanlış'
        ]
        
        result_lower = result.lower()
        
        for keyword in error_keywords:
            if re.search(keyword, result_lower):
                print(f"[DEBUG] Hata algılandı: {keyword}")
                return (True, result)
        
        return (False, result)

    def _execute_tool(self, tool_name: str, args: dict) -> str:
        """Araçları çalıştıran yardımcı metod (dict argümanları alır)."""
        print(f"[DEBUG] Araç çalıştırılıyor: {tool_name}")
        print(f"[DEBUG] Araç argümanları: {args}")
        
        try:
            if tool_name == "write_file":
                filepath = args.get("filepath", "")
                content = args.get("content", "")
                
                if not filepath:
                    return "[ERROR] Hata: Dosya yolu boş. Lütfen geçerli bir dosya yolu sağla."
                
                try:
                    result = write_file(filepath, content)
                    print(f"[DEBUG] write_file başarılı: {filepath}")
                    return result
                except FileNotFoundError:
                    return f"[ERROR] Hata: Dosya yolu yanlış veya dizin bulunamadı: {filepath}"
                except PermissionError:
                    return f"[ERROR] Hata: Dosyaya yazma izni yok: {filepath}"
                except Exception as e:
                    return f"[ERROR] Hata: Dosya yazılamadı: {str(e)}"
            
            elif tool_name == "read_file":
                filepath = args.get("filepath", "")
                if not filepath:
                    return "[ERROR] Hata: Dosya adı boş."
                
                try:
                    print(f"[DEBUG] Agent read_file çağırıyor: {filepath}")
                    result = read_file(filepath)
                    print(f"[DEBUG] read_file başarılı: {filepath}")
                    return result
                except FileNotFoundError:
                    return f"[ERROR] Hata: Dosya bulunamadı: {filepath}"
                except PermissionError:
                    return f"[ERROR] Hata: Dosya okuma izni yok: {filepath}"
                except Exception as e:
                    return f"[ERROR] Hata: Dosya okunamadı: {str(e)}"
            
            elif tool_name == "execute_command":
                command = args.get("command", "")
                if not command:
                    return "[ERROR] Hata: Komut boş."
                
                try:
                    result = execute_command(command)
                    print(f"[DEBUG] execute_command başarılı: {command}")
                    return result
                except Exception as e:
                    return f"[ERROR] Hata: Komut çalıştırılamadı: {str(e)}"
            
            elif tool_name == "search_codebase":
                query = args.get("query", "")
                if not query:
                    return "[ERROR] Hata: Arama sorgusu boş."
                
                try:
                    results = self.retriever.retrieve_relevant_chunks(query)
                    if not results:
                        return "[ERROR] Hata: Arama sonucu bulunamadı. Lütfen sorgu parametrelerini kontrol et."
                    print(f"[DEBUG] search_codebase başarılı: {len(results)} sonuç bulundu")
                    return "\n".join([f"Dosya: {r['file_path']}\nİçerik: {r['text']}" for r in results])
                except Exception as e:
                    return f"[ERROR] Hata: Arama yapılamadı: {str(e)}"
            
            elif tool_name == "git_commit":
                message = args.get("message", "")
                if not message:
                    return "[ERROR] Hata: Commit mesajı boş."
                
                try:
                    result = self.git_tools.git_commit(message)
                    print(f"[DEBUG] git_commit başarılı")
                    return result
                except Exception as e:
                    error_msg = str(e).lower()
                    if "not a git repository" in error_msg:
                        return "[ERROR] Hata: Git yapılandırılmamış. Proje git deposu değil."
                    elif "nothing to commit" in error_msg:
                        return "[ERROR] Hata: Commit yapılacak değişiklik yok."
                    else:
                        return f"[ERROR] Hata: Git commit başarısız oldu: {str(e)}"
            
            elif tool_name == "git_push":
                try:
                    result = self.git_tools.git_push()
                    print(f"[DEBUG] git_push başarılı")
                    return result
                except Exception as e:
                    error_msg = str(e).lower()
                    if "not a git repository" in error_msg:
                        return "[ERROR] Hata: Git yapılandırılmamış."
                    elif "nothing to push" in error_msg:
                        return "[ERROR] Hata: Push yapılacak değişiklik yok."
                    else:
                        return f"[ERROR] Hata: Git push başarısız oldu: {str(e)}"
            
            return f"[ERROR] Hata: Bilinmeyen araç: {tool_name}"
            
        except Exception as e:
            print(f"[DEBUG] Araç çalıştırma hatası: {str(e)}")
            return f"[ERROR] Hata: Araç çalıştırılırken hata oluştu: {str(e)}"

    def ask(self, user_query: str) -> str:
        # Komut kontrolü
        cmd_result = self.handle_command(user_query)
        if cmd_result:
            return cmd_result

        print(f"\nKullanıcı >> {user_query}")
        
        try:
            # 1. LLM'e sor
            print("[DEBUG] LLM'e istek gönderiliyor...")
            response = self.provider_manager.ask(user_query, system_prompt=self.system_prompt)
            print(f"[DEBUG] LLM RAW RESPONSE: {repr(response)}")
            
            # 2. JSON tabanlı araç format'ını parse et
            if "[TOOL_JSON]" in response:
                try:
                    # JSON formatı: [TOOL_JSON]{...}[/TOOL_JSON]
                    match = re.search(r"\[TOOL_JSON\](.*?)\[/TOOL_JSON\]", response, re.DOTALL)
                    if not match:
                        print("[DEBUG] [TOOL_JSON] etiketi bulundu ancak regex eşleşmedi")
                        return response
                    
                    json_str = match.group(1).strip()
                    print(f"[DEBUG] Çıkarılan JSON: {json_str}")
                    
                    # JSON'u parse et
                    try:
                        tool_data = json.loads(json_str)
                    except json.JSONDecodeError as je:
                        print(f"[DEBUG] JSON parse hatası: {je}")
                        return f"[ERROR] Geçersiz JSON formatı: {str(je)}"
                    
                    tool_name = tool_data.get("tool", "")
                    tool_args = tool_data.get("args", {})
                    
                    if not tool_name:
                        return "[ERROR] Hata: Tool adı belirtilmemiş."
                    
                    print(f"[DEBUG] Araç adı: {tool_name}")
                    
                    # Aracı çalıştır
                    result = self._execute_tool(tool_name, tool_args)
                    print(f"[DEBUG] Araç sonucu: {result}")
                    
                    # Araç çıktısında hata var mı kontrol et
                    is_error, error_msg = self._detect_error_in_result(result)
                    
                    if is_error:
                        print("[DEBUG] Araç çalıştırma hatasını algıladı, ajana geri bildiriliyor...")
                        # Hata geri bildirimi (feedback loop)
                        error_feedback = f"[SYSTEM_ERROR] Son yapılan işlem başarısız oldu: {error_msg}. Lütfen hatayı analiz et ve farklı bir yaklaşımla (başka bir araçla veya parametreyle) tekrar dene."
                        print(f"[DEBUG] Sistem hatası mesajı: {error_feedback}")
                        
                        # Ajanı tekrar tetikle
                        print("[DEBUG] Ajana hata ile tekrar soruluyor...")
                        retry_prompt = f"Orijinal talep: '{user_query}'\n\n{error_feedback}"
                        retry_response = self.provider_manager.ask(retry_prompt, system_prompt=self.system_prompt)
                        return retry_response
                    
                    # 3. Başarılı sonucu LLM'e geri gönder ve özetlet
                    final_prompt = f"Kullanıcı sorusu: '{user_query}'.\n\nAraç çalıştırıldı. Sonuç:\n{result}\n\nLütfen bu sonucu kullanıcıya özetle."
                    print("[DEBUG] Araç sonucu LLM'e özetletiliyor...")
                    final_response = self.provider_manager.ask(final_prompt)
                    return final_response
                except json.JSONDecodeError as je:
                    print(f"[DEBUG] JSON decode hatası: {je}")
                    return f"[ERROR] JSON parse edilemedi: {str(je)}"
                except Exception as e:
                    print(f"[DEBUG] Araç ayrıştırma hatası: {e}")
                    traceback.print_exc()
                    return f"[ERROR] Araç çalıştırılamadı: {str(e)}"
            
            print("[WARNING] Model tool çağrısı yapmadı, düz metin döndü.")
            print(f"[DEBUG] Model Yanıtı: {response}")
            return response
            
        except Exception as e:
            print("[DEBUG] !!! HATA YAKALANDI !!!")
            traceback.print_exc()
            return f"HATA: {str(e)}"
