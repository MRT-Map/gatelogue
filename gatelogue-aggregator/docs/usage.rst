Usage
=====

Database
--------

The data is provided in JSON. Its format and description is outlined at :doc:`data_format`.

Raw
+++
Use a HTTP GET request to https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json to retrieve the data.

A version without sources is available, at https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json

gatelogue-types (Python)
++++++++++++++++++++++++
The data can be imported to your Python project in dataclasses.

Run ``pip install git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-types-py`` or add ``gatelogue-types @ git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-types-py`` to your ``requirements.txt`` or ``pyproject.toml``. You can also use ``requests``, ``niquests``, ``httpx``, ``urllib3`` or ``aiohttp`` to retrieve the data via ``gatelogue-types`` if ``[requests]``, ``[niquests]``, ``[httpx]``, ``[urllib3]`` or ``[aiohttp]`` is suffixed. Otherwise ``urllib`` is used.

To retrieve the data:

.. code-block:: python

   import gatelogue_types as gt  # alias highly recommended for convenience's sake

   gt.GatelogueData.get()  # retrieve data, with sources

   gt.GatelogueDataNS.get()  # retrieve data, no sources

   await gt.GatelogueData.aiohttp_get()  # retrieve data, with sources, async

   await gt.GatelogueDataNS.aiohttp_get()  # retrieve data, no sources, async

See :doc:`the API reference for gatelogue_types<_autosummary/gatelogue_types>`.

gatelogue-types (Rust)
++++++++++++++++++++++
See `the docs for gatelogue-types (Rust) <https://mrt-map.github.io/gatelogue/docs/rs>`_.

TypeScript
++++++++++
See https://github.com/MRT-Map/gatelogue/blob/main/gatelogue-client/src/stores/schema.ts for a schema.

CLI
---
The aggregator can be installed wih ``pipx``: ``pipx install git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator``.

See :doc:`cli`.