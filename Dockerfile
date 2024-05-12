FROM python:3.12.2-slim-bookworm

RUN apt-get update;\
    apt-get install -y --no-install-recommends gcc curl gnupg2;\
    apt-get clean;\
    rm -rf /var/lib/apt/lists/*;\
    curl -sSL https://install.python-poetry.org | python3 -;\
    poetry config virtualenvs.create false

ENV PATH="${PATH}:/root/.local/bin"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-dev

COPY src /app

WORKDIR /app

ENTRYPOINT ["uvicorn"]
CMD ["app:app"]
