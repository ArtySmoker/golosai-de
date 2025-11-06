FROM python:3.10-slim

WORKDIR /app

# curl уже есть для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9003"]