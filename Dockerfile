FROM python:3.10-slim-bullseye

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
STOPSIGNAL SIGINT

COPY requirements.txt .

# Install SOAP dependencies
RUN apt-get update && \
    apt-get -yqq upgrade && \
    apt-get install -yqq --no-install-recommends \
        build-essential \
        libxml2 \
        libxmlsec1 \
        libxmlsec1-dev \
        pkg-config && \
    pip install -q --no-cache-dir -r requirements.txt && \
    apt-get remove -yqq --auto-remove \
        build-essential \
        libxmlsec1-dev \
        pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

ENTRYPOINT ["python", "exporter.py"]
