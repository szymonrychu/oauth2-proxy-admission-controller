FROM python:3.12.2-slim-bookworm

COPY requirements.txt /

RUN pip3 install -r /requirements.txt

WORKDIR /app

COPY src /app

ENTRYPOINT ["uvicorn"]
CMD ["app:app"]