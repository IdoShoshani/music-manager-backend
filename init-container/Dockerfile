FROM python:3.9-slim

WORKDIR /app

# Install kubernetes client
RUN pip install kubernetes

# Copy the script
COPY copy_secret.py .

# Run the script
CMD ["python", "copy_secret.py"]