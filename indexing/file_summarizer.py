import groq

class FileSummarizer:
    def summarize_file(self, content: str) -> str:
        """
        Dosya içeriğini özetler.

        Args:
        content (str): Dosya içeriği.

        Returns:
        str: Dosya içeriğinin özetini.
        """
        try:
            prompt = f"Özetle: {content}"
            summary = groq.provider(prompt)
            return summary
        except Exception as e:
            return "Özetleme sırasında hata oluştu: " + str(e)
