# owncloud exporter

## Description

This exporter scrapes the /metrics endpoint of owncloud added by an extension that gives us metrics for users and total storage of the owncloud application.

## Required environment variables

OWNCLOUD_SLEEP_TIME

OWNCLOUD_METRICS_API_KEY

OWNCLOUD_EXPORTER_PORT

OWNCLOUD_URL

## Installation

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

## Compile a binary

pip install pyinstaller

pyinstaller --onefile OwncloudExporter.py

## Usage

python OwncloudExporter.py

## Roadmap

Currently it takes minutes for the metrics endpoint to respond, we are waiting to see if this can be made faster.
