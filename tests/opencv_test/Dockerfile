 FROM python:3.9-slim-bullseye

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    opencv-python-headless \
    numpy

# Set working directory
WORKDIR /app

# Copy the tracking script
COPY yellow_tracker.py .

# Run the script
CMD ["python", "yellow_tracker.py"]FROM python:3.11-slim

