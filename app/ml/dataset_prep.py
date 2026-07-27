import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


DATASET_PATH = "app/dataset/training_data.csv"


def load_dataset():
    """
    Load and preprocess the training dataset.
    """

    df = pd.read_csv(DATASET_PATH)

    # Remove missing values
    df.dropna(inplace=True)

    texts = df["text"].astype(str).tolist()

    label_encoder = LabelEncoder()

    labels = label_encoder.fit_transform(df["category"])

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        label_encoder
    )