#!/usr/bin/env bash
set -euxo pipefail

pipx install git+https://github.com/mrt-map/gatelogue@rewrite#subdirectory=gatelogue-aggregator
gatelogue-aggregator run -o data.json
gatelogue-aggregator schema -o schema.json
git commit -am "update @ $(date +%Y%m%d-%H:%M:%S%Z)"