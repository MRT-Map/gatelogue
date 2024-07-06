#!/usr/bin/env bash
set -euxo pipefail

pipx reinstall gatelogue-aggregator || pipx install --python python3.12 --system-site-packages git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator
until gatelogue-aggregator run -o data.json -g graph.svg "$@"; do
  echo "Retrying in 60s"
  sleep 60
  rm -rf /tmp/gatelogue/wiki-text
  rm -rf /tmp/gatelogue/wiki-html
done
gatelogue-aggregator schema -o schema.json
python3.12 remove_sources.py
git commit -am "update @ $(date +%Y%m%dT%H:%M:%S%Z)"
