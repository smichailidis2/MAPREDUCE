# Use a base Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the master script
COPY master_node.py .

# Specify the default command
# CMD ["tail", "-f", "/dev/null"]
CMD ["sleep", "10000"]