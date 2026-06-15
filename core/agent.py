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
        self.history = [] # Mesaj geçmişi {"role": "user"/"assistant"/"tool"/"system_error", "content": "..."}
        self.MAX_ITERATIONS = 10 # Maksimum adım sayısı

        # Yapay zekaya nasıl davranması gerektiğini dikte eden sistem talimatı
        self.system_prompt = (
            "Sen bir ToolExecutionEngine'sin. Görevin kullanıcıyla sohbet etmek veya açıklama yapmak değil, SADECE araçları tetiklemektir.\n\n"
            "KESİN KURALLAR:\n"
            "1. Yanıtın SADECE ve HER ZAMAN [TOOL_JSON]{...}[/TOOL_JSON] formatında olmalıdır ve içindeki JSON valid olmalıdır.\n"
            "2. Başında veya sonunda hiçbir ek metin, açıklama, 'Tabii', 'İşte kod:' gibi ifadeler OLMAYACAKTIR.\n"
            "3. Kullanıcıya talimat verme, işlemi bizzat yap.\n"
            "4. Tek seferde sadece bir adet [TOOL_JSON] çağrısı yap.\n"
            "5. content alanı dahil TÜM string değerlerdeki özel karakterler (\\n, ', \", [, ], vb.) JSON string olarak otomatik escape edilmelidir.\n"
            "6. Görev birden fazla adım gerektiriyorsa, her adımda bir [TOOL_JSON] çağrısı yap. TÜM adımlar tamamlandığında, [TOOL_JSON] KULLANMADAN düz metinle kullanıcıya özet/sonuç bildir. Bu, görevin bittiğinin işaretidir.\n\n"
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
            r'komut hata ile sonuçlandı', r'başarısız', 
            r'failed', r'bulunamadı', r'not found', r'exception',
            r'traceback', r'errno', r'invalid path', r'yolu yanlış',
            r'error:', r'hata:' # ": " ile daha spesifik eşleşme
        ]
        
        result_lower = result.lower()
        
        for keyword in error_keywords:
            if re.search(keyword, result_lower):
                print(f"[DEBUG] Hata algılandı: '{keyword}'")
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

    def _format_messages_for_llm(self) -> str:
        """
        self.history'deki mesajları LLM'e gönderilecek tek bir prompt string'ine dönüştürür.
        """
        formatted_prompt_parts = []
        
        # Geçmiş konuşmayı history'den ekle
        for msg in self.history:
            if msg["role"] == "user":
                formatted_prompt_parts.append(f"Kullanıcı: {msg['content']}")
            elif msg["role"] == "assistant":
                formatted_prompt_parts.append(f"Asistan: {msg['content']}")
            elif msg["role"] == "tool":
                formatted_prompt_parts.append(f"Araç Sonucu: {msg['content']}")
            elif msg["role"] == "system_error":
                formatted_prompt_parts.append(f"Sistem Hatası: {msg['content']}")
        
        return "\n".join(formatted_prompt_parts)


    def ask(self, user_query: str) -> str:
        cmd_result = self.handle_command(user_query)
        if cmd_result:
            # Komut işlendiyse, history'yi temizle ve komut sonucunu döndür
            self.history = [] 
            return cmd_result

        print(f"\nKullanıcı >> {user_query}")
        self.history.append({"role": "user", "content": user_query})

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            print(f"[DEBUG] Iterasyon {iteration}/{self.MAX_ITERATIONS}")
            
            try:
                # 1. LLM'e sor
                current_prompt = self._format_messages_for_llm()
                print(f"[DEBUG] LLM'e gönderilen prompt (iterasyon {iteration}):\n{current_prompt[:500]}...") # İlk 500 karakteri logla
                response = self.provider_manager.ask(current_prompt, system_prompt=self.system_prompt)
                print(f"[DEBUG] LLM RAW RESPONSE (iterasyon {iteration}): {repr(response)}")
                self.history.append({"role": "assistant", "content": response})

                # 2. JSON tabanlı araç format'ını parse et
                if "[TOOL_JSON]" in response:
                    try:
                        match = re.search(r"\[TOOL_JSON\](.*?)\[/TOOL_JSON\]", response, re.DOTALL)
                        if not match:
                            print("[DEBUG] [TOOL_JSON] etiketi bulundu ancak regex eşleşmedi")
                            # Hata olarak kabul edip modele geri bildirimde bulun
                            error_msg = "[ERROR] Model geçerli bir [TOOL_JSON] formatı döndüremedi. Lütfen düzgün bir [TOOL_JSON] formatı kullan."
                            self.history.append({"role": "system_error", "content": error_msg})
                            continue # Bir sonraki iterasyona geç
                        
                        json_str = match.group(1).strip()
                        print(f"[DEBUG] Çıkarılan JSON (iterasyon {iteration}): {json_str}")
                        
                        try:
                            tool_data = json.loads(json_str)
                        except json.JSONDecodeError as je:
                            error_msg = f"[ERROR] Geçersiz JSON formatı: {str(je)}. Lütfen JSON formatını kontrol et."
                            print(f"[DEBUG] JSON parse hatası (iterasyon {iteration}): {error_msg}")
                            self.history.append({"role": "system_error", "content": error_msg})
                            continue # Bir sonraki iterasyona geç
                        
                        tool_name = tool_data.get("tool", "")
                        tool_args = tool_data.get("args", {})
                        
                        if not tool_name:
                            error_msg = "[ERROR] Hata: Tool adı belirtilmemiş. Lütfen 'tool' alanını doldur."
                            print(f"[DEBUG] Tool adı eksik (iterasyon {iteration}): {error_msg}")
                            self.history.append({"role": "system_error", "content": error_msg})
                            continue # Bir sonraki iterasyona geç
                        
                        print(f"[DEBUG] Araç adı (iterasyon {iteration}): {tool_name}")
                        
                        # Aracı çalıştır
                        result = self._execute_tool(tool_name, tool_args)
                        print(f"[DEBUG] Araç sonucu (iterasyon {iteration}): {result}")
                        
                        # Araç çıktısında hata var mı kontrol et
                        is_error, error_msg_from_tool = self._detect_error_in_result(result)
                        
                        if is_error:
                            print(f"[DEBUG] Araç çalıştırma hatası algılandı (iterasyon {iteration}), ajana geri bildiriliyor...")
                            # Hata geri bildirimi (feedback loop)
                            error_feedback = f"Son yapılan işlem başarısız oldu: {error_msg_from_tool}. Lütfen hatayı analiz et ve farklı bir yaklaşımla (başka bir araçla veya parametreyle) tekrar dene."
                            self.history.append({"role": "system_error", "content": error_feedback})
                            # Döngü devam edecek, LLM bir sonraki iterasyonda hatayı görecek.
                        else:
                            self.history.append({"role": "tool", "content": result})
                            # Başarılı araç çağrısı, döngü devam edecek
                            
                    except Exception as e:
                        print(f"[DEBUG] Araç ayrıştırma veya çalıştırma hatası (iterasyon {iteration}): {e}")
                        traceback.print_exc()
                        self.history.append({"role": "system_error", "content": f"[ERROR] Araç çalıştırılırken genel hata oluştu: {str(e)}"})
                        # Döngü devam edecek
                else:
                    # Model tool çağrısı yapmadıysa, görevin tamamlandığı varsayılır.
                    print(f"[WARNING] Model tool çağrısı yapmadı, düz metin döndü (iterasyon {iteration}). Görev tamamlandı.")
                    final_response_content = response
                    self.history = [] # History'yi temizle
                    return final_response_content
                
            except Exception as e:
                print(f"[DEBUG] !!! HATA YAKALANDI (iterasyon {iteration}) !!!")
                traceback.print_exc()
                self.history = [] # History'yi temizle
                return f"HATA: {str(e)}"
        
        # Maksimum iterasyon sayısına ulaşıldığında
        self.history = [] # History'yi temizle
        return "Maksimum adım sayısına ulaşıldı, görev tamamlanamadı. Lütfen daha küçük adımlarla tekrar dene veya ajana daha net talimatlar ver."
