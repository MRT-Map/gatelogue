use color_eyre::Result;
use common::types::Gate;
use regex::Regex;

use crate::airports::extractor;

pub async fn pce() -> Result<Vec<Gate>> {
    extractor(
        "Peacopolis International Airport",
        "PCE",
        Regex::new(
            r"\n\|(?P<code>[^|]*?)(?:\|\|\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]].*?|)\|\|.*Service",
        )?,
    )
    .await
}

pub async fn mwt() -> Result<Vec<Gate>> {
    extractor(
        "Miu Wan Tseng Tsz Leng International Airport",
        "MWT",
        Regex::new(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|\n)")?,
    )
    .await
}

pub async fn kek() -> Result<Vec<Gate>> {
    extractor(
        "Kazeshima Eumi Konaejima Airport",
        "KEK",
        Regex::new(r"\|(?P<code>[^|}]*?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)\|\|")?,
    )
    .await
}

pub async fn lar() -> Result<Vec<Gate>> {
    extractor(
        "Larkspur Lilyflower International Airport",
        "LAR",
        Regex::new(
            r"(?s)'''(?P<code>[^|]*?)'''\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)\|\|.*?status"
        )?
    ).await
}

pub async fn abg() -> Result<Vec<Gate>> {
    extractor(
        "Antioch-Bay Point Garvey International Airport",
        "ABG",
        Regex::new(
            r"\|(?P<code>.*?\d)\|\| ?(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)(?:\|\||\n)",
        )?,
    )
    .await
}

pub async fn opa() -> Result<Vec<Gate>> {
    extractor(
        "Oparia LeTourneau International Airport",
        "OPA",
        Regex::new(r"\|-\n\|(?P<code>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)")?,
    )
    .await
}

pub async fn chb() -> Result<Vec<Gate>> {
    extractor(
        "Chan Bay Municipal Airport",
        "CHB",
        Regex::new(
            r"\|Gate (?P<code>.*?)\n\|.\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)",
        )?,
    )
    .await
}

pub async fn cbz() -> Result<Vec<Gate>> {
    extractor(
        "Chan Bay Zeta Airport",
        "CBZ",
        Regex::new(r"\|(?P<code>[AB]\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)")?,
    )
    .await
}

pub async fn cbi() -> Result<Vec<Gate>> {
    extractor(
        "Chan Bay International Airport",
        "CBI",
        Regex::new(r"\|(?P<code>\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)")?,
    )
    .await
}
pub async fn dje() -> Result<Vec<Gate>> {
    extractor(
        "Deadbush Johnston-Euphorial Airport",
        "DJE",
        Regex::new(r"\|(?P<code>\d+?)\n\| (?:(?P<airline>[^\n<]*)|[^|]*?)")?,
    )
    .await
}
pub async fn vda() -> Result<Vec<Gate>> {
    extractor(
        "Deadbush Valletta Desert Airport",
        "VDA",
        Regex::new(
            r"\|(?P<code>\d+?)\|\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"
        )?
    ).await
}
pub async fn wmi() -> Result<Vec<Gate>> {
    extractor(
        "West Mesa International Airport",
        "WMI",
        Regex::new(r"\|Gate (?P<code>.*?)\n\| (?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|[^|]*?)")?,
    )
    .await
}
pub async fn dfm() -> Result<Vec<Gate>> {
    extractor(
        "Deadbush Foxfoe Memorial Airport",
        "DFM",
        Regex::new(
            r"\|Gate (?P<code>.*?)\n\|(?P<size>.*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"
        )?
    ).await
}
pub async fn gsm() -> Result<Vec<Gate>> {
    extractor(
        "Gemstride Melodia Airfield",
        "GSM",
        Regex::new(
            r"\|(?P<code>.*?)\n\|'''(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>[^N]\S[^|]*)|[^|]*?)'''"
        )?
    ).await
}
pub async fn vfw() -> Result<Vec<Gate>> {
    extractor(
        "Venceslo-Fifth Ward International Airport",
        "VFW",
        Regex::new(
            r"\|-\n\|(?P<code>\w\d*?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"
        )?
    ).await
}
pub async fn sdz() -> Result<Vec<Gate>> {
    extractor(
        "San Dzobiak International Airport",
        "SDZ",
        Regex::new(
            r"\|-\n\|(?P<code>\w\d+?)\n\|(?:\[\[(?:[^|\]]*?\|)?(?P<airline>.*?)]]|(?P<airline2>\S[^|]*)|[^|]*?)"
        )?
    ).await
}
