import argparse
import re
import sys
from pathlib import Path

import yaml

ALLOWED_ENVS = {"dev", "staging", "prod"}
ALLOWED_REGIONS = {"europe-west2", "europe-west1", "europe-west4"}
ALLOWED_MACHINE_TYPES = {
    "n1-standard-4",
    "n1-standard-8",
    "e2-standard-4",
    "e2-standard-8",
}
MAX_DISK_GB = 500
MAX_TTL_HOURS = 168  # 7 days
MIN_IDLE_SHUTDOWN_MINUTES = 10
MAX_IDLE_SHUTDOWN_MINUTES = 480

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{2,29}$")  # 3-30 chars, k8s-ish


def fail(msg: str) -> None:
    print(f"VALIDATION_ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_yaml(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        fail(f"Request file not found: {path}")
    except yaml.YAMLError as e:
        fail(f"Invalid YAML in {path}: {e}")


def get(d: dict, dotted: str, default=None):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def validate(path: Path) -> None:
    req = load_yaml(path)

    name = req.get("name")
    if not name or not isinstance(name, str) or not NAME_RE.match(name):
        fail("name must match ^[a-z][a-z0-9-]{2,29}$ (3-30 chars, lowercase, hyphen allowed)")

    env = req.get("env")
    if env not in ALLOWED_ENVS:
        fail(f"env must be one of {sorted(ALLOWED_ENVS)}")

    region = req.get("region")
    if region not in ALLOWED_REGIONS:
        fail(f"region must be one of {sorted(ALLOWED_REGIONS)}")

    owner = req.get("owner")
    if not owner or not isinstance(owner, str) or len(owner) < 3:
        fail("owner must be a non-empty string")

    team = req.get("team")
    if not team or not isinstance(team, str) or len(team) < 2:
        fail("team must be a non-empty string")

    mt = get(req, "workbench.machine_type")
    if mt not in ALLOWED_MACHINE_TYPES:
        fail(f"workbench.machine_type must be one of {sorted(ALLOWED_MACHINE_TYPES)}")

    disk = get(req, "workbench.disk_gb")
    if not isinstance(disk, int) or disk < 50 or disk > MAX_DISK_GB:
        fail(f"workbench.disk_gb must be an int between 50 and {MAX_DISK_GB}")

    disable_public_ip = get(req, "workbench.disable_public_ip")
    if disable_public_ip is not True:
        fail("workbench.disable_public_ip must be true (public IPs are not allowed)")

    idle = get(req, "workbench.idle_shutdown_minutes")
    if not isinstance(idle, int) or not (MIN_IDLE_SHUTDOWN_MINUTES <= idle <= MAX_IDLE_SHUTDOWN_MINUTES):
        fail(f"workbench.idle_shutdown_minutes must be {MIN_IDLE_SHUTDOWN_MINUTES}-{MAX_IDLE_SHUTDOWN_MINUTES}")

    ttl = req.get("ttl_hours")
    if not isinstance(ttl, int) or ttl < 1 or ttl > MAX_TTL_HOURS:
        fail(f"ttl_hours must be an int between 1 and {MAX_TTL_HOURS}")

    labels = req.get("labels")
    if not isinstance(labels, dict) or not labels:
        fail("labels must be a non-empty map")
    required_labels = {"app", "cost_center", "owner", "env"}
    missing = required_labels - set(labels.keys())
    if missing:
        fail(f"labels missing required keys: {sorted(missing)}")
    if labels.get("env") != env:
        fail("labels.env must match top-level env")

    print("OK")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True, help="Path to request YAML")
    args = p.parse_args()
    validate(Path(args.file))


if __name__ == "__main__":
    main()
