#!/usr/bin/env bash
set -euxo pipefail

uv tool install -Up 3.14 git+https://github.com/mrt-map/gatelogue@v3#subdirectory=gatelogue-aggregator
rm ./data.db ./data-ns.db
gatelogue-aggregator run "$@"
gatelogue-aggregator drop-sources
