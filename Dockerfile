FROM python:3.11-slim

WORKDIR /app

# copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy flight test script
COPY tests/test_codrone.py .

# run script automatically
CMD ["python", "test_codrone.py"]
