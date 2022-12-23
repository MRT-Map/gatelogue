use color_eyre::Result;
use common::types::Gate;
use regex::Regex;

use crate::airlines::extract;

pub async fn astrella() -> Result<Vec<(Gate, Gate, String)>> {
    extract("Astrella", Regex::new(r"\{\{AstrellaFlight\|code = (?P<code>[^$\n]*?)\|airport1 = (?P<a1>[^\n]*?)\|gate1 = (?P<g1>[^\n]*?)\|airport2 = (?P<a2>[^\n]*?)\|gate2 = (?P<g2>[^\n]*?)\|size = (?P<s>[^\n]*?)\|status = active}}")?).await
}
