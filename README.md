![](https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/main/gatelogue-client/public/gat2-light.png)

![Github Version](https://img.shields.io/github/v/release/MRT-Map/gatelogue)
![Docs Status](https://img.shields.io/github/actions/workflow/status/MRT-Map/gatelogue/.github%2Fworkflows%2Fpages.yml?style=flat&label=docs&link=https%3A%2F%2Fmrt-map.github.io%2Fgatelogue%2Fdocs)
![GitHub License](https://img.shields.io/github/license/MRT-Map/gatelogue)
![GitHub Pages Status](https://img.shields.io/github/actions/workflow/status/MRT-Map/gatelogue/.github%2Fworkflows%2Fpages.yml?style=flat&label=website&link=https%3A%2F%2Fmrt-map.github.io%2Fgatelogue)

![GitHub code size](https://img.shields.io/github/languages/code-size/MRT-Map/gatelogue)
![GitHub repo size](https://img.shields.io/github/repo-size/MRT-Map/gatelogue)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/mrt-map/gatelogue/main)
![GitHub commits since latest release (branch)](https://img.shields.io/github/commits-since/mrt-map/gatelogue/latest/main?include_prereleases)
![GitHub Release Date](https://img.shields.io/github/release-date/MRT-Map/gatelogue)

![GitHub last commit (branch)](https://img.shields.io/github/last-commit/mrt-map/gatelogue/dist?label=last%20data%20update)

`gatelogue-types` (python):
![PyPI - Version](https://img.shields.io/pypi/v/gatelogue-types)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gatelogue-types)
![Docs Status](https://img.shields.io/github/actions/workflow/status/MRT-Map/gatelogue/.github%2Fworkflows%2Fpages.yml?style=flat&label=docs&link=https%3A%2F%2Fmrt-map.github.io%2Fgatelogue%2Fdocs%2F_autosummary%2Fgatelogue_types.html)
![PyPI - Downloads](https://img.shields.io/pypi/dm/gatelogue-types)
![Pepy Total Downlods](https://img.shields.io/pepy/dt/gatelogue-types)

`gatelogue-types` (rust):
![Crates.io Version](https://img.shields.io/crates/v/gatelogue-types)
![Crates.io MSRV](https://img.shields.io/crates/msrv/gatelogue-types)
![Docs Status](https://img.shields.io/github/actions/workflow/status/MRT-Map/gatelogue/.github%2Fworkflows%2Fpages.yml?style=flat&label=local%20docs&link=https%3A%2F%2Fmrt-map.github.io%2Fgatelogue%2Fdocs%2Frs)
![docs.rs](https://img.shields.io/docsrs/gatelogue-types?label=docs.rs)
![Crates.io Downloads (recent)](https://img.shields.io/crates/dr/gatelogue-types)
![Crates.io Total Downloads](https://img.shields.io/crates/d/gatelogue-types)

`gatelogue-types` (ts, npm):
![NPM Version](https://img.shields.io/npm/v/gatelogue-types)
![Docs Status](https://img.shields.io/github/actions/workflow/status/MRT-Map/gatelogue/.github%2Fworkflows%2Fpages.yml?style=flat&label=typedoc&link=https%3A%2F%2Fmrt-map.github.io%2Fgatelogue%2Fdocs%2Fts)
![NPM Downloads](https://img.shields.io/npm/dw/gatelogue-types?label=downloads%20(week))
![NPM Downloads](https://img.shields.io/npm/dy/gatelogue-types?label=downloads%20(year))

`gatelogue-types` (ts, jsr):
![JSR Version](https://img.shields.io/jsr/v/@mrt-map/gatelogue-types)

Database of air, rail, sea, bus routes on the [Minecart Rapid Transit server](https://minecartrapidtransit.net).

Data is aggregated by `gatelogue-aggregator`, as shown by `gatelogue-client` at https://mrt-map.github.io/gatelogue (air only). The data can then be retrieved in your application with `gatelogue-types` (py, rs, ts)

Docs for the aggregator, data format, and type libraries are located at https://mrt-map.github.io/gatelogue/docs

<!-- TODO: rework dev container
## development setup
if you want to use a github codespace, just open one! setup is handled for you, and will take a few minutes. (it's the green code button, under the codespaces tab)

if you'd rather do things locally, the easiest way to get started is with dev containers:

1. install docker
2. install the [remote development pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) for vscode
3. Use Cmd/Ctrl + Shift + P -> 'Clone Repository in Container Volume' to clone this repo (don't use 'reopen in container', as that will conflict with pnpm)
4. the container will take a few minutes to install and set up

congrats! you did it!

run the aggregator with the command `gatelogue-aggregator run`

run the client with the command `cd gatelogue-client` and `pnpm run dev`
-->