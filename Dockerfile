FROM alpine:3.15.0

COPY . .
WORKDIR /

RUN apk add --no-cache python3 py3-pip
RUN apk add build-base

RUN apk add --no-cache supervisor \
    && python3 -m pip install --upgrade pip \
    && pip install -r /requirements.txt


# CMD ["python3", "main.py"]
# EXPOSE 8000