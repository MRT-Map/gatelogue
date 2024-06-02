/* eslint-disable */
export default {
  $ref: "#/$defs/gatelogue_aggregator.types.context.Context.SerializableClass",
  $defs: {
    "gatelogue_aggregator.types.context.Context.SerializableClass": {
      title: "SerializableClass",
      type: "object",
      properties: {
        flight: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Flight.SerializableClass",
          },
        },
        airport: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Airport.SerializableClass",
          },
        },
        gate: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Gate.SerializableClass",
          },
        },
        airline: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Airline.SerializableClass",
          },
        },
      },
      required: ["flight", "airport", "gate", "airline"],
    },
    "gatelogue_aggregator.types.air.Flight.SerializableClass": {
      title: "SerializableClass",
      type: "object",
      properties: {
        codes: { type: "array", items: { type: "string" } },
        gates: {
          type: "array",
          items: { $ref: "#/$defs/SerializableClass_str_" },
        },
        airline: { $ref: "#/$defs/SerializableClass_str_" },
      },
      required: ["codes", "gates", "airline"],
    },
    SerializableClass_str_: {
      title: "SerializableClass[str]",
      type: "object",
      properties: {
        v: { type: "string" },
        s: { type: "array", items: { type: "string" } },
      },
      required: ["v", "s"],
    },
    "gatelogue_aggregator.types.air.Airport.SerializableClass": {
      title: "SerializableClass",
      type: "object",
      properties: {
        code: { type: "string" },
        name: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/SerializableClass_str_" }],
        },
        world: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/SerializableClass_str_" }],
        },
        coordinates: {
          anyOf: [
            { type: "null" },
            { $ref: "#/$defs/SerializableClass_tuple_int__int__" },
          ],
        },
        link: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/SerializableClass_str_" }],
        },
        gates: {
          type: "array",
          items: { $ref: "#/$defs/SerializableClass_str_" },
        },
      },
      required: ["code", "name", "world", "coordinates", "link", "gates"],
    },
    SerializableClass_tuple_int__int__: {
      title: "SerializableClass[tuple[int, int]]",
      type: "object",
      properties: {
        v: {
          type: "array",
          minItems: 2,
          maxItems: 2,
          prefixItems: [{ type: "integer" }, { type: "integer" }],
          items: false,
        },
        s: { type: "array", items: { type: "string" } },
      },
      required: ["v", "s"],
    },
    "gatelogue_aggregator.types.air.Gate.SerializableClass": {
      title: "SerializableClass",
      type: "object",
      properties: {
        code: { anyOf: [{ type: "string" }, { type: "null" }] },
        flights: {
          type: "array",
          items: { $ref: "#/$defs/SerializableClass_str_" },
        },
        airport: { $ref: "#/$defs/SerializableClass_str_" },
        airline: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/SerializableClass_str_" }],
        },
        size: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/SerializableClass_str_" }],
        },
      },
      required: ["code", "flights", "airport", "airline", "size"],
    },
    "gatelogue_aggregator.types.air.Airline.SerializableClass": {
      title: "SerializableClass",
      type: "object",
      properties: {
        name: { type: "string" },
        flights: {
          type: "array",
          items: { $ref: "#/$defs/SerializableClass_str_" },
        },
        link: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/SerializableClass_str_" }],
        },
      },
      required: ["name", "flights", "link"],
    },
  },
} as const;
