# Use a base Python image
FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the master script
COPY run_client.py .

# Specify the default command
CMD ["python", "run_client.py"]