FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ARG INSTALL_EXTRAS=""

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY LICENSE README.md MANIFEST.in pyproject.toml setup.py ./
COPY src ./src
COPY main.py process_ds_jobs.py runtime.example.toml ./

RUN python -m pip install --upgrade pip \
    && if [ -n "$INSTALL_EXTRAS" ]; then pip install ".[$INSTALL_EXTRAS]"; else pip install .; fi

VOLUME ["/app/artifacts"]

ENTRYPOINT ["linkedin-webscraper"]
CMD ["scrape", "daily"]
