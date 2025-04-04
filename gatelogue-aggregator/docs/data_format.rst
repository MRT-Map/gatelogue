Data Format
===========

If you use `JSON schemas <https://json-schema.org/>`_, see https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/schema.json.

If you use `Typescript <https://www.typescriptlang.org/>`_, see https://github.com/MRT-Map/gatelogue/blob/main/gatelogue-client/src/stores/schema.ts for Typescript types.

Specification
-------------
* **All links below reference their entries in the full reference page. These classes are here for convenience's sake.**
* **Do not hardcode any IDs in your project!** They change with every update. If you need to reference a specific object, find it by its code/name/something unique to the object.
* Check the ``version`` field in the ``Context`` object for the data format version. We will try our best to maintain backwards-compatibility, but we cannot guarantee.
* The JSON file at `data.json <https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json>`_ is of base type ``Context``.
* If you are using `data_no_sources.json <https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json>`_, all instances of ``Sourced[T]`` below are replaced with just the encapsulated type ``T``.

  * If you are using the Typescript types referenced above, the type for the JSON of the no-source version is ``GatelogueData<false>`` instead of simply ``GatelogueData`` or ``GatelogueData<true>``.

* ``Context.Export`` can be called ``Data`` in your project.
* :py:class:`tuple` and :py:class:`set` serialise to a list.
* ``None`` serialises to ``null``.

The current data format version is

.. program-output:: python -c "from gatelogue_aggregator.__about__ import __version__; print('v'+__version__.split('+')[1])"

.. autoclass:: gatelogue_aggregator.types.context.context::Context.Export
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.base::Node
   :members:
   :inherited-members:
   :no-index:

Air Nodes
+++++++++

.. autoclass:: gatelogue_aggregator.types.node.air::AirFlight
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirAirport
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirGate
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirAirline
   :members:
   :inherited-members:
   :no-index:

Rail Nodes
++++++++++

.. autoclass:: gatelogue_aggregator.types.node.rail::RailCompany
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.rail::RailLine
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.rail::RailStation
   :members:
   :inherited-members:
   :no-index:

Sea Nodes
+++++++++

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaCompany
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaLine
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaStop
   :members:
   :inherited-members:
   :no-index:

Bus Nodes
+++++++++

.. autoclass:: gatelogue_aggregator.types.node.bus::BusCompany
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.bus::BusLine
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.bus::BusStop
   :members:
   :inherited-members:
   :no-index:

Town Nodes
++++++++++

.. autoclass:: gatelogue_aggregator.types.node.town::Town
   :members:
   :inherited-members:
   :no-index:

Miscellaneous
+++++++++++++

.. autoclass:: gatelogue_aggregator.types.source::Sourced
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.connections::Connection
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.connections::Direction
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.context.proximity::Proximity
   :members:
   :inherited-members:
   :no-index:

.. autoclass:: gatelogue_aggregator.types.context.shared_facility::SharedFacility
   :members:
   :inherited-members:
   :no-index:

