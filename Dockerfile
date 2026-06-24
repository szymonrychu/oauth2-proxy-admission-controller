FROM python:3.14.6-slim-bookworm@sha256:4ff4b92a68355dbdb52584ab3391dff8d371a61d4e063468bfd0130e3189c6d9 AS global_dependencies

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
