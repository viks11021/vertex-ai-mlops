# Vertex AI MLOps Demo – Self-Serve Training & Deployment

This repository demonstrates a **production-style MLOps workflow on Google Vertex AI** where **data scientists can train, register, deploy, and serve models without managing VMs**.

All infrastructure, scaling, and serving is handled by **Vertex AI**.  
Users interact only through **Docker, GCS, and Vertex AI APIs**.

---

## Architecture Flow
Data (GCS)
↓
Vertex AI Custom Training Job
↓
Model Artifacts (GCS)
↓
Vertex AI Model Registry
↓
Vertex AI Endpoint
↓
Online Predictions (REST / SDK)

---

## Repository Structure
vertex-ai-mlops/
├── docker/
│   ├── training.Dockerfile
│   └── serving.Dockerfile
├── src/
│   ├── training/
│   │   └── train.py
│   ├── evaluation/
│   │   └── evaluate.py
│   ├── inference/
│   │   ├── predict.py
│   │   └── predict_vertex.py
│   └── common/
├── data/
│   └── raw/
│       └── train.csv
├── requirements.txt
├── requirements-serving.txt
├── request.json
└── README.md

---

## Prerequisites

- Google Cloud Project
- Vertex AI API enabled
- Artifact Registry enabled
- Docker with `buildx`
- Authenticated `gcloud`

```bash
gcloud auth login
gcloud config set project <PROJECT_ID>

gcloud services enable \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com


Python Dependencies

Training (requirements.txt)
pandas
numpy<2
scikit-learn==1.3.2
joblib==1.3.2
pyyaml
google-cloud-storage
google-auth
google-cloud-aiplatform

Serving (requirements-serving.txt)

numpy<2
scikit-learn==1.3.2
joblib==1.3.2
google-cloud-aiplatform


⸻

Step 1: Create Artifact Registry

gcloud artifacts repositories create mlops-images \
  --repository-format=docker \
  --location=europe-west2 \
  --description="Docker images for Vertex AI MLOps demo"


⸻

Step 2: Build & Push Training Image

Vertex AI requires linux/amd64 images.

docker buildx build \
  --platform linux/amd64 \
  -f docker/training.Dockerfile \
  -t europe-west2-docker.pkg.dev/$PROJECT_ID/mlops-images/training:v5 \
  --push .

Verify:

gcloud artifacts docker images list \
  europe-west2-docker.pkg.dev/$PROJECT_ID/mlops-images


⸻

Step 3: Create GCS Bucket & Upload Data

export BUCKET="gs://$PROJECT_ID-vertex-mlops-demo"

gcloud storage buckets create "$BUCKET" \
  --location=europe-west2

gcloud storage cp data/raw/train.csv \
  "$BUCKET/data/raw/train.csv"


⸻

Step 4: Run Training on Vertex AI

gcloud ai custom-jobs create \
  --region=europe-west2 \
  --display-name=mlops-demo-train-gcs-v5 \
  --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri=europe-west2-docker.pkg.dev/$PROJECT_ID/mlops-images/training:v5 \
  --args="--data-path=$BUCKET/data/raw/train.csv","--model-dir=$BUCKET/artifacts/models/vertex/v5"

Check status:

gcloud ai custom-jobs list --region=europe-west2


⸻

Step 5: Verify Model Artifact

gsutil ls -lh "$BUCKET/artifacts/models/vertex/v5/"

Expected:

model.joblib


⸻

Step 6: Upload Model to Vertex AI Registry

export REGION="europe-west2"
export MODEL_DIR="$BUCKET/artifacts/models/vertex/v5"
export MODEL_DISPLAY_NAME="mlops-demo-sklearn-v5"

gcloud ai models upload \
  --region="$REGION" \
  --display-name="$MODEL_DISPLAY_NAME" \
  --artifact-uri="$MODEL_DIR" \
  --container-image-uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"

Get model ID:

gcloud ai models list \
  --region="$REGION" \
  --filter="displayName=$MODEL_DISPLAY_NAME" \
  --format="value(name)"


⸻

Step 7: Create Endpoint

gcloud ai endpoints create \
  --region="$REGION" \
  --display-name="mlops-demo-endpoint-v5"

Get endpoint ID:

gcloud ai endpoints list \
  --region="$REGION" \
  --format="value(name)"


⸻

Step 8: Deploy Model to Endpoint

gcloud ai endpoints deploy-model \
  "projects/$PROJECT_NUM/locations/$REGION/endpoints/<ENDPOINT_ID>" \
  --region="$REGION" \
  --model="projects/$PROJECT_NUM/locations/$REGION/models/<MODEL_ID>" \
  --display-name="sklearn-v5-deployed" \
  --machine-type="n1-standard-4" \
  --min-replica-count=1 \
  --max-replica-count=1

Verify deployment:

gcloud ai endpoints describe \
  "projects/$PROJECT_NUM/locations/$REGION/endpoints/<ENDPOINT_ID>" \
  --region="$REGION"


⸻

Step 9: Online Prediction (CLI)

Create request:

cat > request.json <<EOF
{
  "instances": [
    [1, 10],
    [2, 20],
    [5, 50]
  ]
}
EOF

Predict:

gcloud ai endpoints predict \
  "projects/$PROJECT_NUM/locations/$REGION/endpoints/<ENDPOINT_ID>" \
  --region="$REGION" \
  --json-request=request.json

Output:

[0, 0, 1]


⸻

Step 10: Online Prediction (Python SDK)

python src/inference/predict_vertex.py \
  --project "$PROJECT_ID" \
  --region "europe-west2" \
  --endpoint-id "<ENDPOINT_ID>" \
  --instances '[[1,10],[2,20],[5,50]]'

Output:

[0.0, 0.0, 1.0]


⸻

Key Outcomes
	•	No VM provisioning
	•	Fully containerised training
	•	GCS-backed model artifacts
	•	Vertex AI Model Registry
	•	Online serving via managed endpoints
	•	Safe versioning and rollback

⸻

What This Demonstrates

This demo shows how a platform team enables true self-serve MLOps:
	•	Data scientists focus only on code and data
	•	Platform handles infra, scale, and security
	•	CI/CD friendly and production ready

⸻

Future Enhancements
	•	CI/CD with GitHub Actions
	•	Model evaluation gates
	•	Canary / shadow deployments
	•	Vertex Pipelines (KFP)
	•	Feature Store integration

---

