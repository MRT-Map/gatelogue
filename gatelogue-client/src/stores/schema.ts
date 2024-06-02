/* eslint-disable */
export default {
  $ref: "#/$defs/gatelogue_aggregator.types.context.Context.Ser",
  $defs: {
    "gatelogue_aggregator.types.context.Context.Ser": {
      title: "Ser",
      type: "object",
      properties: {
        flight: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Flight.Ser",
          },
        },
        airport: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Airport.Ser",
          },
        },
        gate: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Gate.Ser",
          },
        },
        airline: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/gatelogue_aggregator.types.air.Airline.Ser",
          },
        },
      },
      required: ["flight", "airport", "gate", "airline"],
    },
    "gatelogue_aggregator.types.air.Flight.Ser": {
      title: "Ser",
      type: "object",
      properties: {
        codes: { type: "array", items: { type: "string" } },
        gates: {
          type: "array",
          items: { $ref: "#/$defs/Ser_str_" },
        },
        airline: { $ref: "#/$defs/Ser_str_" },
      },
      required: ["codes", "gates", "airline"],
    },
    Ser_str_: {
      title: "Ser[str]",
      type: "object",
      properties: {
        v: { type: "string" },
        s: { type: "array", items: { type: "string" } },
      },
      required: ["v", "s"],
    },
    "gatelogue_aggregator.types.air.Airport.Ser": {
      title: "Ser",
      type: "object",
      properties: {
        code: { type: "string" },
        name: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_str_" }],
        },
        world: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_str_" }],
        },
        coordinates: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_tuple_int__int__" }],
        },
        link: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_str_" }],
        },
        gates: {
          type: "array",
          items: { $ref: "#/$defs/Ser_str_" },
        },
      },
      required: ["code", "name", "world", "coordinates", "link", "gates"],
    },
    Ser_tuple_int__int__: {
      title: "Ser[tuple[int, int]]",
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
    "gatelogue_aggregator.types.air.Gate.Ser": {
      title: "Ser",
      type: "object",
      properties: {
        code: { anyOf: [{ type: "string" }, { type: "null" }] },
        flights: {
          type: "array",
          items: { $ref: "#/$defs/Ser_str_" },
        },
        airport: { $ref: "#/$defs/Ser_str_" },
        airline: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_str_" }],
        },
        size: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_str_" }],
        },
      },
      required: ["code", "flights", "airport", "airline", "size"],
    },
    "gatelogue_aggregator.types.air.Airline.Ser": {
      title: "Ser",
      type: "object",
      properties: {
        name: { type: "string" },
        flights: {
          type: "array",
          items: { $ref: "#/$defs/Ser_str_" },
        },
        link: {
          anyOf: [{ type: "null" }, { $ref: "#/$defs/Ser_str_" }],
        },
      },
      required: ["name", "flights", "link"],
    },
  },
} as const;
