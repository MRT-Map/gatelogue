#!/usr/bin/env bash
set -euxo pipefail

pipx reinstall gatelogue-aggregator || pipx install --python python3.12 git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator
gatelogue-aggregator run -o data.json
gatelogue-aggregator schema -o schema.json
git commit -am "update @ $(date +%Y%m%d-%H:%M:%S%Z)"
