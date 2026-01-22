import argparse
import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

def train(data_path: str, model_dir: str):
    df = pd.read_csv(data_path)
    X = df[["feature1", "feature2"]]
    y = df["target"]

    model = LogisticRegression()
    model.fit(X, y)

    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_path)

    print(f"Model trained and saved to {model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default="data/raw/train.csv")
    parser.add_argument("--model-dir", default="models")
    args = parser.parse_args()

    train(args.data_path, args.model_dir)