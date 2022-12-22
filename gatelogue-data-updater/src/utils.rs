use color_eyre::{eyre::eyre, Result};
use mediawiki::{api::Api, page::Page, title::Title};

pub async fn wikitext(page: &str) -> Result<String> {
    let api = Api::new("https://wiki.minecartrapidtransit.net/api.php").await?;
    let title = Title::new_from_full(page, &api);
    let page = Page::new(title);
    Ok(page.text(&api).await.map_err(|e| eyre!("{e:#?}"))?)
}
