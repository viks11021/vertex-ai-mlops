# Vertex AI MLOps Demo (Sklearn + Custom Job + Endpoint)

End-to-end demo:
1) Train a simple sklearn model on Vertex AI Custom Jobs
2) Store artifacts in GCS
3) Upload model to Vertex AI Model Registry
4) Deploy to a Vertex AI Endpoint
5) Run an online prediction smoke test

## Prereqs
- gcloud SDK authenticated
- Project: `adroit-goods-485117-k2`
- Region: `europe-west2`
- Docker (for building training image)
- Python 3.11 (optional for local run)

## Repo structure
- `src/training/train.py` — trains model, writes/exports `model.joblib`
- `src/evaluation/evaluate.py` — local eval (optional)
- `docker/training.Dockerfile` — training container
- `scripts/smoke_predict.sh` — endpoint prediction test

## One-time setup
```bash
gcloud config set project adroit-goods-485117-k2
gcloud services enable aiplatform.googleapis.com artifactregistry.googleapis.com storage.googleapis.com