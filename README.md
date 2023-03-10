# owncloud exporter

## Description

This exporter scrapes the /metrics endpoint of owncloud added by an extension that gives us metrics for users and total storage of the owncloud application.

## Required environment variables

OWNCLOUD_SLEEP_TIME

OWNCLOUD_METRICS_API_KEY

OWNCLOUD_EXPORTER_PORT

OWNCLOUD_URL

## Installation
export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib
python3.7 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python3.7 exporter.py


* If you run on CentOS 7 and don't have Python 3.7, you will need to compile it from source:
```
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
tar xzf Python-3.7.0.tgz
./configure --enable-optimizations --with-threads --enable-shared
make
make install altinstall
```

=======

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

## Compile a binary

## Package the software as a binary
pyinstaller exporter.py --onefile 

The generated binary is under ./dist/ directory.

## Systemd unit

```
[Unit]
Description=Prometheus Owncloud Exporter

[Service]
Environment=OWNCLOUD_URL=https://myserver.domain.org
Environment=OWNCLOUD_SLEEP_TIME=43200
Environment=OWNCLOUD_METRICS_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXX
ExecStart=/usr/local/bin/owncloud-exporter
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
```
=======
pip install pyinstaller

pyinstaller --onefile OwncloudExporter.py

## Usage

python OwncloudExporter.py

## Roadmap

Currently it takes minutes for the metrics endpoint to respond, we are waiting to see if this can be made faster.
