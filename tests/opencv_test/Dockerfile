FROM python:3.9-slim

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --force-reinstall numpy
RUN pip install opencv-python-headless


WORKDIR /app
COPY yellow_tracker.py .

CMD ["bash"]
