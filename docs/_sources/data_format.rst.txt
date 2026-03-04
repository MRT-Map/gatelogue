Data Format
===========

Check the ``version`` field under ``Metadata`` for the data format version. We will try our best to maintain backwards-compatibility, but we cannot guarantee.

The current data format version is

.. program-output:: python -c "from gatelogue_aggregator.__about__ import __data_version__; print('v'+str(__data_version__))"


.. literalinclude:: ../../gatelogue-types-py/src/gatelogue_types/create.sql
   :language: sql
