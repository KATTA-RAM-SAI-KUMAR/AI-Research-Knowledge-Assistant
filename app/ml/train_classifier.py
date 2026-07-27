import os
import pickle
import numpy as np
import tensorflow as tf

from tensorflow.keras import layers, models
from app.ml.dataset_prep import load_dataset


MODEL_DIR = "models"

MODEL_PATH = os.path.join(MODEL_DIR, "tf_classifier.h5")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")


def train():

    os.makedirs(MODEL_DIR, exist_ok=True)

    X_train, X_test, y_train, y_test, label_encoder = load_dataset()

    X_train = np.array(X_train, dtype=object)
    X_test = np.array(X_test, dtype=object)

    vectorizer = layers.TextVectorization(
        max_tokens=10000,
        output_mode="int",
        output_sequence_length=100
    )

    vectorizer.adapt(X_train)

    vocabulary = vectorizer.get_vocabulary()

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vocabulary, f)

    X_train = vectorizer(X_train)
    X_test = vectorizer(X_test)

    num_classes = len(label_encoder.classes_)

    model = models.Sequential([

        layers.Input(shape=(100,), dtype=tf.int64),

        layers.Embedding(
            input_dim=len(vocabulary),
            output_dim=64,
            mask_zero=True
        ),

        layers.GlobalAveragePooling1D(),

        layers.Dense(
            128,
            activation="relu"
        ),

        layers.Dropout(0.3),

        layers.Dense(
            num_classes,
            activation="softmax"
        )

    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    print("\nTraining Started...\n")

    model.fit(
        X_train,
        y_train,
        validation_data=(X_test, y_test),
        epochs=10,
        batch_size=16,
        verbose=1
    )

    print("\nEvaluating Model...\n")

    loss, accuracy = model.evaluate(
        X_test,
        y_test,
        verbose=1
    )

    print(f"\nTest Accuracy : {accuracy:.4f}")

    model.save(MODEL_PATH)

    with open(LABEL_ENCODER_PATH, "wb") as f:
        pickle.dump(label_encoder, f)

    print("\n==============================")
    print("Training Completed")
    print("==============================")
    print("Model :", MODEL_PATH)
    print("Labels:", LABEL_ENCODER_PATH)
    print("Vocabulary:", VECTORIZER_PATH)


if __name__ == "__main__":
    train()