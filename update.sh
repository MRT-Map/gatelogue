#!/usr/bin/env bash
set -euxo pipefail

pipx install --python python3.12 --force git+https://github.com/mrt-map/gatelogue@rewrite#subdirectory=gatelogue-aggregator
~/.local/share/pipx/venvs/gatelogue-aggregator/bin/gatelogue-aggregator run -o data.json
~/.local/share/pipx/venvs/gatelogue-aggregator/bin/gatelogue-aggregator schema -o schema.json
git commit -am "update @ $(date +%Y%m%d-%H:%M:%S%Z)"
