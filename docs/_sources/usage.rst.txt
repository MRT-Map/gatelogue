Usage
=====

Data
----

The data is provided in JSON. Its format and description is outlined at :doc:`data_format`.

Raw
+++
Use a HTTP GET request to https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json to retrieve the data.

A version without sources is available, at https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json

gatelogue-types (Python)
++++++++++++++++++++++++
The data can be imported to your Python project in ``msgspec`` dataclasses. Run ``pip install gatelogue-types`` or add ``gatelogue-types`` to your ``requirements.txt`` or ``pyproject.toml``.

(To import directly from the repository, run ``pip install git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-types-py`` or add ``gatelogue-types @ git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-types-py`` to your ``requirements.txt`` or ``pyproject.toml``.)

You can also use ``requests``, ``niquests``, ``httpx``, ``urllib3`` or ``aiohttp`` to retrieve the data via ``gatelogue-types`` if ``[requests]``, ``[niquests]``, ``[httpx]``, ``[urllib3]`` or ``[aiohttp]`` is suffixed. Otherwise ``urllib`` is used.

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

gatelogue-types (TypeScript)
++++++++++
See `the docs for gatelogue-types (TypeScript) <https://mrt-map.github.io/gatelogue/docs/ts>`_.

Aggregator
----------
The aggregator can be installed wih ``pipx`` (regular ``pip`` is fine too): ``pipx install git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator``.

See :doc:`cli`.