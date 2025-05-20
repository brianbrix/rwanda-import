FROM python:3.10-slim

WORKDIR /app


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY . .

CMD ["python", "import.py"]
