FROM python:3.7-alpine

# Build tools
RUN apk --update add \
  build-base \
  gcc \
  git \
  libffi-dev \
  openssl-dev \
  && rm -rf /var/cache/apk/*

# Setup
ENV appdir /usr/src/app
RUN mkdir -p ${appdir}
WORKDIR ${appdir}

# Auth
ENV GMAIL_USERNAME "sample"
ENV GMAIL_PASSWORD "sample"

# Dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt \
  && pip install aioimaplib aiosmtplib

# Install and Run
ADD ex_pub.py .
ADD ex_consumer.py .
ADD config.json .

RUN ["python3", "ex_consumer.py"]
