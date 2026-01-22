import argparse
import os
import tempfile
from urllib.parse import urlparse

import pandas as pd
from joblib import dump
from sklearn.linear_model import LogisticRegression

from google.cloud import storage


def is_gcs(path: str) -> bool:
    return path.startswith("gs://")


def parse_gcs_uri(uri: str):
    u = urlparse(uri)
    bucket = u.netloc
    blob = u.path.lstrip("/")
    return bucket, blob


def download_from_gcs(gcs_uri: str) -> str:
    bucket_name, blob_name = parse_gcs_uri(gcs_uri)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    local_path = os.path.join(tempfile.gettempdir(), os.path.basename(blob_name) or "input.csv")
    blob.download_to_filename(local_path)
    return local_path


def upload_to_gcs(local_path: str, gcs_uri: str) -> None:
    bucket_name, blob_name = parse_gcs_uri(gcs_uri)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", required=True, help="Local path or gs:// bucket path to training CSV")
    parser.add_argument("--model-dir", required=True, help="Local dir or gs:// prefix to store model")
    args = parser.parse_args()

    data_path = download_from_gcs(args.data_path) if is_gcs(args.data_path) else args.data_path

    df = pd.read_csv(data_path)
    X = df[["feature1", "feature2"]]
    y = df["target"]

    model = LogisticRegression()
    model.fit(X, y)

    # Always write locally first
    local_model_dir = tempfile.mkdtemp(prefix="model-")
    local_model_path = os.path.join(local_model_dir, "model.joblib")
    dump(model, local_model_path)

    if is_gcs(args.model_dir):
        # Treat model-dir as a prefix like gs://bucket/path/models
        out_uri = args.model_dir.rstrip("/") + "/model.joblib"
        upload_to_gcs(local_model_path, out_uri)
        print(f"Model trained and uploaded to {out_uri}")
    else:
        os.makedirs(args.model_dir, exist_ok=True)
        final_path = os.path.join(args.model_dir, "model.joblib")
        os.replace(local_model_path, final_path)
        print(f"Model trained and saved to {final_path}")


if __name__ == "__main__":
    main()