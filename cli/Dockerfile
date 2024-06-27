FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY mapreduce-cli.py .
COPY generate_input.py .
RUN python generate_input.py

# Run the CLI tool when the container launches
ENTRYPOINT ["python", "mapreduce_cli.py"]
