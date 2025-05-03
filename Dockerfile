FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7002

CMD ["python", "api.py"]