# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize synthetic database and model on build/entry
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose FastAPI and Streamlit ports
EXPOSE 8000 8501

# Default command launches backend and frontend via helper script
CMD ["sh", "-c", "python scripts/initialize_db.py && python scripts/train_model.py && python scripts/build_knowledge_base.py && uvicorn app.api.main:app --host 0.0.0.0 --port 8000 & streamlit run app/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
