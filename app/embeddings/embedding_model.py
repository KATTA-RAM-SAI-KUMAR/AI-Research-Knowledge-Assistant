from fastembed import TextEmbedding


class EmbeddingModel:
    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None:
            print("Loading FastEmbed embedding model...")

            self.model = TextEmbedding(
                model_name="BAAI/bge-small-en-v1.5"
            )

            print("FastEmbed embedding model loaded.")

    def embed(self, text):
        self._load_model()

        if isinstance(text, str):
            return list(self.model.embed([text]))[0].tolist()

        return [
            vector.tolist()
            for vector in self.model.embed(text)
        ]