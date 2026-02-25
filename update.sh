#!/usr/bin/env bash
set -euxo pipefail

pipx reinstall gatelogue-aggregator || pipx install --system-site-packages git+https://github.com/mrt-map/gatelogue@v3#subdirectory=gatelogue-aggregator
gatelogue-aggregator run "$@"
gatelogue-aggregator drop-sources
