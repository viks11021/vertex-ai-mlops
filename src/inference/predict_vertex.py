import argparse
import json
from google.cloud import aiplatform


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--region", required=True)
    p.add_argument("--endpoint-id", required=True, help="Numeric endpoint id, e.g. 8486120903128645632")
    p.add_argument("--instances", required=True, help='JSON string, e.g. "[[1,10],[2,20]]"')
    return p.parse_args()


def main():
    args = parse_args()

    aiplatform.init(project=args.project, location=args.region)
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{args.project}/locations/{args.region}/endpoints/{args.endpoint_id}"
    )

    instances = json.loads(args.instances)
    preds = endpoint.predict(instances=instances)

    # Vertex returns a Prediction object; print clean JSON for demos/CI
    print(json.dumps(preds.predictions))


if __name__ == "__main__":
    main()
