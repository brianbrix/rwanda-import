FROM python:3.6-alpine

WORKDIR /app


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --progress-bar off -r requirements.txt

COPY . .

CMD ["python", "importer.py"]
