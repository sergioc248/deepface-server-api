FROM --platform=linux/arm64 python:3.9-slim-bullseye

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel support
RUN pip install --upgrade pip setuptools wheel

# Install TensorFlow for ARM (use pip - works!)
RUN pip install tensorflow==2.10.1

# Install all other Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY ./app ./app

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
