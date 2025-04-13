#!/usr/bin/env bash
set -euxo pipefail

pipx reinstall gatelogue-aggregator || pipx install --system-site-packages git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator
gatelogue-aggregator run -o data.json -g graph.svg "$@"
gatelogue-aggregator schema -o schema.json
python remove_sources.py
