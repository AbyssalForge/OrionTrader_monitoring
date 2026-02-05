FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webhook_forwarder.py .

EXPOSE 9094

CMD ["python", "webhook_forwarder.py"]
