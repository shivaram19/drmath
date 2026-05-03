FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY pipeline/ ./pipeline/
COPY web/ ./web/
COPY data/ ./data/ 2>/dev/null || true
COPY output/ ./output/ 2>/dev/null || true
COPY test_pipeline.py ./

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "-m", "uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]
