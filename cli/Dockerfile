FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY mapreduce-cli.py .

RUN chmod +x mapreduce-cli.py

CMD ["python", "mapreduce-cli.py"]