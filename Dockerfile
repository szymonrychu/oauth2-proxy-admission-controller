FROM python:3.12.4-slim-bookworm@sha256:da2d7af143dab7cd5b0d5a5c9545fe14e67fc24c394fcf1cf15e8ea16cbd8637 as global_dependencies

ARG INSTALL_DEV=false

RUN pip install poetry

WORKDIR /app

FROM global_dependencies as dependencies

COPY pyproject.toml poetry.lock* /app/

RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install ; else poetry install --without=dev ; fi"

COPY oauth2_proxy_admission_controller /app/oauth2_proxy_admission_controller

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
