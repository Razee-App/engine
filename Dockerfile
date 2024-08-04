FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/conf.d /etc/nginx/conf.d

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
