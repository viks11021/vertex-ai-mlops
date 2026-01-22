import argparse
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score

def evaluate(data_path: str, model_path: str):
    df = pd.read_csv(data_path)
    X = df[["feature1", "feature2"]]
    y = df["target"]

    model = joblib.load(model_path)
    preds = model.predict(X)

    acc = accuracy_score(y, preds)
    print(f"Accuracy: {acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default="data/raw/train.csv")
    parser.add_argument("--model-path", default="models/model.joblib")
    args = parser.parse_args()

    evaluate(args.data_path, args.model_path)