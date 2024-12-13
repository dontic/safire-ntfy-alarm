# Dockerfile
FROM python:3.11-bullseye

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run as non-root user for security
RUN useradd -m appuser
USER appuser

CMD ["python", "main.py"]