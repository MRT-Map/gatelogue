Data Format
===========

If you use `JSON schemas <https://json-schema.org/>`_, see https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/schema.json.

If you use `Typescript <https://www.typescriptlang.org/>`_, see https://github.com/MRT-Map/gatelogue/blob/main/gatelogue-client/src/stores/schema.ts for Typescript types.

Specification
-------------
* **All links below reference their entries in the full reference page. These classes are here for convenience's sake.**
* **Do not hardcode any UUIDs in your project!** They change with every update. If you need to reference a specific object, find it by its code/name/something unique to the object.
* Check the ``version`` field in the ``Context`` object for the specification version. **The current version is v1.** We will try our best to maintain backwards-compatibility, but we cannot guarantee.
* The JSON file at `data.json <https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json>`_ is of base type ``Context``.
* If you are using `data_no_sources.json <https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json>`_, all instances of ``Sourced[T]`` or ``Sourced.Ser[T]`` below are replaced with just the encapsulated type ``T``.

  * If you are using the Typescript types referenced above, the type for the JSON of the no-source version is ``GatelogueData<false>`` instead of simply ``GatelogueData`` or ``GatelogueData<true>``.

* Most objects here have a ``.Ser`` prefix because they are the serialised versions of their original classes. However in your own projects a ``Ser`` suffix is unnecessary.
* ``Context`` objects can be called ``Data`` in your project.
* :py:class:`uuid.UUID` serialises to a string, eg. ``0b0e1f74-3683-4ff2-aa51-a13587950c56``
* :py:class:`tuple` and :py:class:`set` serialise to a list.
* ``None`` serialises to ``null``.

.. autoclass:: gatelogue_aggregator.types.context::Context.Ser
   :members:
   :undoc-members:
   :inherited-members:
   :no-index:

Air
+++

.. autoclass:: gatelogue_aggregator.types.node.air::AirContext.Ser
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirFlight.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirAirport.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirGate.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.air::AirAirline.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

Rail
++++

.. autoclass:: gatelogue_aggregator.types.node.rail::RailContext.Ser
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.rail::RailCompany.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.rail::RailLine.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.rail::RailStation.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

Sea
+++

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaContext.Ser
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaCompany.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaLine.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.sea::SeaStop.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

Bus
+++

.. autoclass:: gatelogue_aggregator.types.node.bus::BusContext.Ser
   :members:
   :undoc-members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.bus::BusCompany.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.bus::BusLine.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.node.bus::BusStop.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

Miscellaneous
+++++++++++++
.. autoclass:: gatelogue_aggregator.types.base::Sourced.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.connections::Connection.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.connections::Direction.Ser
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index:

.. autoclass:: gatelogue_aggregator.types.connections::Proximity
   :members:
   :inherited-members:
   :exclude-members: uuid, Literal
   :no-index: