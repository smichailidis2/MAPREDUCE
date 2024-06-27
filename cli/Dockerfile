FROM python:3.12-alpine

WORKDIR /app

COPY mapreduce_cli.py .
COPY requirements.txt .
COPY input_data.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Run the CLI tool when the container launches
ENTRYPOINT ["python", "mapreduce_cli.py"]
