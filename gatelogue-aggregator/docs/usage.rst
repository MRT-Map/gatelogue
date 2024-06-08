Usage
=====

Database
--------

Use a HTTP GET request to https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json to retrieve the data.

A version without sources is available, at https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json

The data is provided in JSON. Its format and description is outlined at :doc:`data_format`.

CLI
---
The aggregator can be installed wih ``pipx``: ``pipx install --python python3.12 git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator``.

See :doc:`cli`.