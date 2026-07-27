import requests


class OllamaClient:

    MODEL = "llama3.2"

    @staticmethod
    def generate(prompt: str):

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OllamaClient.MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 700
                }
            },
            timeout=300
        )

        response.raise_for_status()

        return response.json()["response"]