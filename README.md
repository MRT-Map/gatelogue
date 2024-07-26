![](./gatelogue-client/public/gat2-light.png)

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

Database of air, rail, sea, bus routes on the MRT

Client is hosted at https://mrt-map.github.io/gatelogue

Documentation for the aggregator and data format is located at https://mrt-map.github.io/gatelogue/docs

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
