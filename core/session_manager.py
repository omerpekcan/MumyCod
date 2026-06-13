from typing import List, Dict, Any

class SessionManager:
    """
    MumyCod'un kullanıcıyla olan anlık sohbet geçmişini (Session) 
    hafızada tutan ve yöneten şef sınıf.
    """
    
    def __init__(self, system_prompt: str = "Sen yardımsever bir yazılım asistanısın."):
        self.system_prompt = system_prompt
        self.history: List[Dict[str, str]] = []
        self.reset_session()

    def reset_session(self):
        """Sohbet geçmişini sıfırlar ve sistem promptunu en başa koyar."""
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

    def add_user_message(self, message: str):
        """Kullanıcının yazdığı mesajı hafızaya ekler."""
        self.history.append({"role": "user", "content": message})

    def add_agent_message(self, message: str):
        """Yapay zekanın verdiği cevabı hafızaya ekler."""
        self.history.append({"role": "assistant", "content": message})

    def get_messages(self) -> List[Dict[str, str]]:
        """LLM sağlayıcısına gönderilmeye hazır tüm geçmişi döner."""
        return self.history