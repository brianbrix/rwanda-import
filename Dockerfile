
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install system dependencies (if any).  For pandas, no system-level
# dependencies are strictly required, but if you needed something
# like libpq-dev for psycopg2, you'd add it here with apt-get.
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     <system_dependency_1> \
#     <system_dependency_2> \
#     && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to manage dependencies
RUN python -m venv /venv
# Make sure pip and setuptools are up to date.
RUN /venv/bin/pip install --upgrade pip setuptools

# Install Python dependencies from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN /venv/bin/pip install --no-cache-dir --progress-bar off -r requirements.txt

# Expose the port your application runs on (if applicable)
# EXPOSE 8000

# Set the command to run your application
CMD ["/venv/bin/python", "import.py"] #Or gunicorn, or whatever your entrypoint is
