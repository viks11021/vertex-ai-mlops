FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/

# Default command (Vertex will override args, but this works locally too)
ENTRYPOINT ["python", "src/training/train.py"]