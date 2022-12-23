use color_eyre::Result;
use common::types::Gate;
use regex::Regex;

use crate::airlines::extract;

pub async fn astrella() -> Result<Vec<(Gate, Gate, String)>> {
    extract(
        "Astrella",
        "Astrella",
        "",
        Regex::new(r"\{\{AstrellaFlight\|code = (?P<code>[^$\n]*?)\|airport1 = (?P<a1>[^\n]*?)\|gate1 = (?P<g1>[^\n]*?)\|airport2 = (?P<a2>[^\n]*?)\|gate2 = (?P<g2>[^\n]*?)\|size = (?P<s>[^\n]*?)\|status = active}}")?
    ).await
}

pub async fn turbula() -> Result<Vec<(Gate, Gate, String)>> {
    extract(
        "Turbula",
        "Template:TurbulaFlightList",
        "",
        Regex::new(r"code = (?P<code>LU\d*).*?(?:\n.*?)?airport1 = (?P<a1>.*?) .*?airport2 = (?P<a2>.*?) .*?status = active")?
    ).await
}

pub async fn blu_air() -> Result<Vec<(Gate, Gate, String)>> {
    extract(
        "BluAir",
        "List of BluAir flights",
        "",
        Regex::new(r"\{\{BA\|(?P<code>.*?)\|(?P<a1>.*?)\|(?P<a2>.*?)\|.*?\|.*?\|(?P<g1>.*?)\|(?P<g2>.*?)\|a\|.*?\|.}}")?
    ).await
}

pub async fn intra_air() -> Result<Vec<(Gate, Gate, String)>> {
    extract( // TODO deal with Terminal X gate X format
        "IntraAir",
        "IntraAir/Flight List",
        "IA",
        Regex::new(r"Flight (?P<code>.*?)}}.*?\n.*?'''(?P<a1>.*?)'''.*?\n.*?'''(?P<a2>.*?)'''.*?\n.*?\n.*?\n.*?open.*?\n.*?\n.*?\n.*?'''(?P<g1>[^']*?)'''\n.*?'''(?P<g2>[^']*?)'''\n")?
    ).await
}

pub async fn fli_high() -> Result<Vec<(Gate, Gate, String)>> {
    extract(
        "FliHigh",
        "FliHigh Airlines",
            "",
        Regex::new(r"\{\{FHList\|(?P<code>.*?)\|(?P<a1>.*?)\|(?P<a2>.*?)\|.*?\|.*?\|(?P<g1>.*?)\|(?P<g2>.*?)\|a\|.*?\|FH}}")?
    ).await
}

pub async fn ola() -> Result<Vec<(Gate, Gate, String)>> {
    extract(
        "Oceanic Langus Airways",
        "Template:AerL",
        "",
        Regex::new(r"'''(?P<code>.*?)'''.*?\n.*?'''(?P<a1>.*?)'''.*?\n.*?\n.*?'''(?P<a2>.*?)'''.*?\n.*?\n.*?Active")?
    ).await
}
