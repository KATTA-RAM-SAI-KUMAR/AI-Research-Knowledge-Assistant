import os
import requests
from groq import Groq


class OllamaClient:

    # Local Ollama model
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Cloud model used when GROQ_API_KEY is available
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    @staticmethod
    def generate(prompt: str):

        groq_api_key = os.getenv("GROQ_API_KEY")

        # ---------------------------------------------------------
        # CLOUD MODE: Groq
        # ---------------------------------------------------------
        if groq_api_key:
            client = Groq(api_key=groq_api_key)

            response = client.chat.completions.create(
                model=OllamaClient.GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_completion_tokens=700,
            )

            return response.choices[0].message.content

        # ---------------------------------------------------------
        # LOCAL MODE: Ollama
        # ---------------------------------------------------------
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OllamaClient.OLLAMA_MODEL,
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