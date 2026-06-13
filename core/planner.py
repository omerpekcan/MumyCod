class Planner:

    def plan(self, prompt: str) -> dict:

        prompt_lower = prompt.lower()

        code_words = [
            "düzenle",
            "değiştir",
            "ekle",
            "sil",
            "refactor",
            "güncelle"
        ]

        if any(word in prompt_lower for word in code_words):

            return {
                "intent": "modify_code",
                "query": prompt
            }

        return {
            "intent": "question",
            "query": prompt
        }