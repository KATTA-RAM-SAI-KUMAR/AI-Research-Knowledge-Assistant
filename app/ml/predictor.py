import pickle
import numpy as np


MODEL_PATH = "models/tf_classifier.h5"
LABEL_ENCODER_PATH = "models/label_encoder.pkl"
VECTORIZER_PATH = "models/vectorizer.pkl"


class DocumentClassifier:

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.vectorizer = None
        self._loaded = False

    def _load_model(self):

        if self._loaded:
            return

        print("Loading TensorFlow document classifier...")

        # Import TensorFlow only when classification is actually needed
        import tensorflow as tf
        from tensorflow.keras.layers import TextVectorization

        self.model = tf.keras.models.load_model(MODEL_PATH)

        with open(LABEL_ENCODER_PATH, "rb") as f:
            self.label_encoder = pickle.load(f)

        with open(VECTORIZER_PATH, "rb") as f:
            vocabulary = pickle.load(f)

        self.vectorizer = TextVectorization(
            max_tokens=10000,
            output_mode="int",
            output_sequence_length=100,
            vocabulary=vocabulary
        )

        self._loaded = True

        print("TensorFlow document classifier loaded successfully.")

    def predict(self, text: str):

        if text is None or text.strip() == "":
            return "Unknown"

        self._load_model()

        vectorized = self.vectorizer(
            np.array([text], dtype=object)
        )

        prediction = self.model.predict(
            vectorized,
            verbose=0
        )

        predicted_index = np.argmax(prediction)

        predicted_category = self.label_encoder.inverse_transform(
            [predicted_index]
        )[0]

        return predicted_category


classifier = DocumentClassifier()