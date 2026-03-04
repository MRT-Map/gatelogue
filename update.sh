#!/usr/bin/env bash
set -euxo pipefail

uv tool install -Up 3.14 git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator
rm ./data.db ./data-ns.db
gatelogue-aggregator run "$@" | tee log.log
gatelogue-aggregator drop-sources
