import re
import os
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
            "Sen bir yazılım ajanı değilsin, sen bir ToolExecutionEngine'sin. "
            "Kullanıcıdan bir dosya okuma veya yazma talebi geldiğinde, kesinlikle kendi kendine cevap verme. "
            "Cevabın ZORUNLU OLARAK sadece [TOOL:arac_adi(argumanlar)] formatında başlamalıdır. "
            "Eğer bu formatta cevap vermezsen kullanıcı işlemini gerçekleştiremez. "
            "Asla rol yapma, işlemi gerçekleştirmek için gerekli aracı tetikle.\n\n"
            "ARAÇLAR:\n"
            "1. Dosya oluşturmak veya güncellemek için `write_file(filepath, content)` aracını kullanabilirsin.\n"
            "2. Mevcut bir dosyayı okumak için `read_file(filepath)` aracını kullanabilirsin.\n"
            "3. Terminal komutu çalıştırmak için `execute_command(command)` aracını kullanabilirsin.\n"
            "4. Kod tabanında arama yapmak için `search_codebase(query)` aracını kullanabilirsin.\n"
            "5. Git commit yapmak için `git_commit(message)` aracını kullanabilirsin.\n"
            "6. Git push yapmak için `git_push()` aracını kullanabilirsin.\n"
            "Bunu kullanmak için yanıtında şu formatı kullan:\n"
            "[TOOL:write_file(dosya_yolu, içerik)] veya [TOOL:read_file(dosya_yolu)] veya [TOOL:execute_command(komut)] veya [TOOL:search_codebase(sorgu)] veya [TOOL:git_commit(mesaj)] veya [TOOL:git_push()]"
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

    def _execute_tool(self, tool_call: str) -> str:
        """Araçları çalıştıran yardımcı metod."""
        print(f"[DEBUG] Araç çalıştırılıyor: {tool_call}")
        
        try:
            if "(" not in tool_call or ")" not in tool_call:
                return "[ERROR] Hata: Geçersiz araç formatı."
            
            tool_name = tool_call.split('(')[0].strip()
            tool_args = tool_call.split('(', 1)[1].rsplit(')', 1)[0].strip()
            
            print(f"[DEBUG] Tetiklenen Araç: {tool_name}")
            print(f"[DEBUG] Temizlenmiş Argümanlar: {tool_args}")
            
            if tool_name == "write_file":
                parts = tool_args.split(',', 1)
                if len(parts) == 2:
                    path = parts[0].replace('path=', '').strip().strip("'").strip('"')
                    content = parts[1].replace('content=', '').strip().strip("'").strip('"')
                    
                    if not path:
                        return "[ERROR] Hata: Dosya yolu boş. Lütfen geçerli bir dosya yolu sağla."
                    
                    try:
                        result = write_file(path, content)
                        print(f"[DEBUG] write_file başarılı: {path}")
                        return result
                    except FileNotFoundError:
                        return f"[ERROR] Hata: Dosya yolu yanlış veya dizin bulunamadı: {path}"
                    except PermissionError:
                        return f"[ERROR] Hata: Dosyaya yazma izni yok: {path}"
                    except Exception as e:
                        return f"[ERROR] Hata: Dosya yazılamadı: {str(e)}"
                return "[ERROR] Hata: write_file için dosya_yolu ve içerik gerekli."
            
            elif tool_name == "read_file":
                filename = tool_args.replace('filename=', '').strip("'").strip('"')
                if not filename:
                    return "[ERROR] Hata: Dosya adı boş."
                
                try:
                    result = read_file(filename)
                    print(f"[DEBUG] read_file başarılı: {filename}")
                    return result
                except FileNotFoundError:
                    return f"[ERROR] Hata: Dosya bulunamadı: {filename}"
                except PermissionError:
                    return f"[ERROR] Hata: Dosya okuma izni yok: {filename}"
                except Exception as e:
                    return f"[ERROR] Hata: Dosya okunamadı: {str(e)}"
            
            elif tool_name == "execute_command":
                command = tool_args.strip("'").strip('"')
                if not command:
                    return "[ERROR] Hata: Komut boş."
                
                try:
                    result = execute_command(command)
                    print(f"[DEBUG] execute_command başarılı: {command}")
                    return result
                except Exception as e:
                    return f"[ERROR] Hata: Komut çalıştırılamadı: {str(e)}"
            
            elif tool_name == "search_codebase":
                query = tool_args.strip("'").strip('"')
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
                message = tool_args.strip("'").strip('"')
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
            response = self.provider_manager.ask(user_query)
            print(f"[DEBUG] LLM'den gelen ham cevap: {response}")
            
            # 2. Araçları basitçe parse et
            if "[TOOL:" in response:
                try:
                    # [TOOL:name(args)] -> name(args)
                    tool_call = response.split("[TOOL:")[1].split("]")[0]
                    
                    # Aracı çalıştır
                    result = self._execute_tool(tool_call)
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
                        retry_response = self.provider_manager.ask(retry_prompt)
                        return retry_response
                    
                    # 3. Başarılı sonucu LLM'e geri gönder ve özetlet
                    final_prompt = f"Kullanıcı sorusu: '{user_query}'.\n\nAraç çalıştırıldı. Sonuç:\n{result}\n\nLütfen bu sonucu kullanıcıya özetle."
                    print("[DEBUG] Araç sonucu LLM'e özetletiliyor...")
                    final_response = self.provider_manager.ask(final_prompt)
                    return final_response
                except Exception as e:
                    print(f"[DEBUG] Araç ayrıştırma hatası: {e}")
                    return f"[ERROR] Araç çalıştırılamadı: {str(e)}"
            
            print("[DEBUG] Araç tespit edilmedi, doğrudan yanıt dönülüyor.")
            return response
            
        except Exception as e:
            print("[DEBUG] !!! HATA YAKALANDI !!!")
            traceback.print_exc()
            return f"HATA: {str(e)}"
