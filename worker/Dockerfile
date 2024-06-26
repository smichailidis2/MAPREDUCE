# Use a base Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the worker script
COPY worker_node.py .

# Specify the default command
CMD ["python", "worker_node.py"]
