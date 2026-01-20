# Unite-I - Open Source Fact-Checking Service
# https://github.com/UniteSocial/Unite-I
#
# This Dockerfile creates reproducible builds for SHA-256 verification.
# Build hash can be compared against the public repository to verify
# that the deployed code matches the open-source version.

FROM python:3.13-slim

# Build arguments for version tracking
ARG BUILD_DATE
ARG GIT_COMMIT
ARG VERSION=2.0.0

# Labels for image metadata
LABEL org.opencontainers.image.title="Unite-I"
LABEL org.opencontainers.image.description="Open-source AI-powered fact-checking service"
LABEL org.opencontainers.image.source="https://github.com/UniteSocial/Unite-I"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY prompts/ ./prompts/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
