FROM python:3.12-alpine

WORKDIR /app

RUN apk add gcc g++ musl-dev python3-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
