FROM python:3.11-slim

# Create non-root user with same UID as host (1000) so bind mounts work
RUN groupadd -r -g 1000 appgroup && useradd -r -u 1000 -g appgroup appuser

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
COPY db/ ./db/
COPY pipeline/ ./pipeline/
COPY web/ ./web/
COPY data/ ./data/
COPY output/ ./output/
COPY test_pipeline.py ./

# Ensure data dir exists and is owned by appuser
RUN mkdir -p data output && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "-m", "uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]
