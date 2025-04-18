Data Format
===========

If you use `JSON schemas <https://json-schema.org/>`_, see https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/schema.json.

If you use `Typescript <https://www.typescriptlang.org/>`_, see https://github.com/MRT-Map/gatelogue/blob/main/gatelogue-client/src/stores/schema.ts for Typescript types.

Specification
-------------
* **All links below reference their entries in the full reference page. These classes are here for convenience's sake.**
* **Do not hardcode any IDs in your project!** They change with every update. If you need to reference a specific object, find it by its code/name/something unique to the object.
* Check the ``version`` field in the ``GatelogueData`` object for the data format version. We will try our best to maintain backwards-compatibility, but we cannot guarantee.
* The JSON file at `data.json <https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json>`_ is of base type ``GatelogueData``.
* If you are using `data_no_sources.json <https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json>`_, all instances of ``Sourced[T]`` below are replaced with just the encapsulated type ``T``.

  * If you are using ``gatelogue-types`` (Python), each object has a No-Source equivalent. The types for these objects have an ``NS`` suffix.
  * If you are using the Typescript types referenced above, the type for the JSON of the no-source version is ``GatelogueData<false>`` instead of simply ``GatelogueData`` or ``GatelogueData<true>``.

* :py:class:`tuple` and :py:class:`set` serialise to a list.
* ``None`` serialises to ``null``.

The current data format version is

.. program-output:: python -c "from gatelogue_aggregator.__about__ import __version__; print('v'+__version__.split('+')[1])"

.. py:currentmodule:: gt

.. autoclass:: gatelogue_types::GatelogueData
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::Node
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::LocatedNode
   :show-inheritance:
   :members:
   :no-index:

Air Nodes
+++++++++

.. autoclass:: gatelogue_types::AirFlight
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::AirAirport
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::AirGate
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::AirAirline
   :show-inheritance:
   :members:
   :no-index:

Rail Nodes
++++++++++

.. autoclass:: gatelogue_types::RailCompany
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::RailLine
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::RailStation
   :show-inheritance:
   :members:
   :no-index:

Sea Nodes
+++++++++

.. autoclass:: gatelogue_types::SeaCompany
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::SeaLine
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::SeaStop
   :show-inheritance:
   :members:
   :no-index:

Bus Nodes
+++++++++

.. autoclass:: gatelogue_types::BusCompany
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::BusLine
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::BusStop
   :show-inheritance:
   :members:
   :no-index:

Town Nodes
++++++++++

.. autoclass:: gatelogue_types::Town
   :show-inheritance:
   :members:
   :no-index:

Miscellaneous
+++++++++++++

.. autoclass:: gatelogue_types::Sourced
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::Connection
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::Direction
   :show-inheritance:
   :members:
   :no-index:

.. autoclass:: gatelogue_types::Proximity
   :show-inheritance:
   :members:
   :no-index:
