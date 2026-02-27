Usage
=====

Data
----

Gatelogue data is compiled into a SQLite database. Its schema / data format is at :doc:`data_format`.

.. important::
   **Do not hardcode any IDs in your project!** They change with every update.
   If you need to reference a specific object, find it by its code/name/something unique to the object.

Raw
+++
.. todo

Use a HTTP GET request to https://raw.githubusercontent.com/MRT-Map/gatelogue/dist-v3/data-ns.db to retrieve the data.

A version with sources is available, at https://raw.githubusercontent.com/MRT-Map/gatelogue/dist-v3/data.db

gatelogue-types (Python)
++++++++++++++++++++++++
See :doc:`the API reference for gatelogue_types<_autosummary/gatelogue_types>`.

gatelogue-types (Rust)
++++++++++++++++++++++
See `the docs for gatelogue-types (Rust) <https://mrt-map.github.io/gatelogue/docs/rs>`_.

gatelogue-types (TypeScript)
++++++++++
See `the docs for gatelogue-types (TypeScript) <https://mrt-map.github.io/gatelogue/docs/ts>`_.

Aggregator
----------
The aggregator can be installed wih ``pipx`` (``pip`` or ``uvx`` is fine too): ``pipx install git+https://github.com/mrt-map/gatelogue#subdirectory=gatelogue-aggregator``.

See :doc:`cli`.