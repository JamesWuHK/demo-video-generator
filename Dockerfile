FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[api]"

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy source code
COPY src/ src/
COPY examples/ examples/

# Create output directory
RUN mkdir -p /app/output

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "demo_video_generator.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
