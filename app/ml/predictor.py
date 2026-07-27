import pickle
import numpy as np
import tensorflow as tf

from tensorflow.keras.layers import TextVectorization


MODEL_PATH = "models/tf_classifier.h5"
LABEL_ENCODER_PATH = "models/label_encoder.pkl"
VECTORIZER_PATH = "models/vectorizer.pkl"


class DocumentClassifier:

    def __init__(self):

        # Load trained model
        self.model = tf.keras.models.load_model(MODEL_PATH)

        # Load label encoder
        with open(LABEL_ENCODER_PATH, "rb") as f:
            self.label_encoder = pickle.load(f)

        # Load saved vocabulary
        with open(VECTORIZER_PATH, "rb") as f:
            vocabulary = pickle.load(f)

        # Recreate TextVectorization layer
        self.vectorizer = TextVectorization(
            max_tokens=10000,
            output_mode="int",
            output_sequence_length=100,
            vocabulary=vocabulary
        )

    def predict(self, text: str):

        if text is None or text.strip() == "":
            return "Unknown"

        # Vectorize text
        vectorized = self.vectorizer(
            np.array([text], dtype=object)
        )

        # Predict
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