FROM python:3.14.2-slim-bookworm@sha256:adb6bdfbcc7c744c3b1a05976136555e2d82b7df01ac3efe71737d7f95ef0f2d AS global_dependencies

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
