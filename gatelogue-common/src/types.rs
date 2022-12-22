use arrayvec::ArrayString;
use petgraph::prelude::UnGraph;
use serde::{Deserialize, Serialize};
use smol_str::SmolStr;

pub type AirportCode = ArrayString<4>;
pub type FlightNo = SmolStr;
pub type GateCode = SmolStr;

pub type Graph = UnGraph<Gate, Flight>;

#[derive(Clone, Debug, Eq, Serialize, Deserialize)]
pub struct Gate {
    pub airport: AirportCode,
    pub gate_code: GateCode,
    pub recorded_airline: Option<SmolStr>,
    pub size: Option<SmolStr>,
}
impl PartialEq for Gate {
    fn eq(&self, other: &Self) -> bool {
        self.airport == other.airport && self.gate_code == other.gate_code
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Flight {
    pub flight_no: FlightNo,
    pub airline: SmolStr,
}
