FROM python:3.14.4-slim-bookworm@sha256:336220baf4dc02a9da56db1720ce6d248aa7c62a0445af0ea1876ae76cc99bed AS global_dependencies

ARG INSTALL_DEV=false

RUN pip install poetry

WORKDIR /app

FROM global_dependencies AS dependencies

COPY README.md pyproject.toml poetry.lock* /app/

COPY oauth2_proxy_admission_controller /app/oauth2_proxy_admission_controller

RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install ; else poetry install --without=dev ; fi"

ENV PYTHONPATH=/app

CMD ["poetry", "run", "python", "oauth2_proxy_admission_controller/main.py"]





# RUN apt-get update;\
#     apt-get install -y --no-install-recommends gcc curl gnupg2;\
#     apt-get clean;\
#     rm -rf /var/lib/apt/lists/*;\
#     curl -sSL https://install.python-poetry.org | python3 -;\
#     poetry config virtualenvs.create false

# ENV PATH="${PATH}:/root/.local/bin"

# COPY pyproject.toml poetry.lock* ./

# RUN poetry install --no-root --no-dev

# COPY src /app

# WORKDIR /app

# ENTRYPOINT ["uvicorn"]
# CMD ["app:app"]
