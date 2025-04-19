/* eslint-disable no-use-before-define,@typescript-eslint/no-unused-vars */
// noinspection JSUnusedGlobalSymbols
export class GD {
    data;
    constructor(data) {
        this.data = data;
    }
    static async get() {
        return new GD(await fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json").then((res) => res.json()));
    }
    static async getNoSources() {
        return new GD(await fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json").then((res) => res.json()));
    }
    node(id) {
        return this.data.nodes[id];
    }
    get nodes() {
        return Object.values(this.data.nodes);
    }
    airFlight(id) {
        return this.node(id);
    }
    get airFlights() {
        return this.nodes.filter((a) => a.type === "AirFlight");
    }
    airAirport(id) {
        return this.node(id);
    }
    get airAirports() {
        return this.nodes.filter((a) => a.type === "AirAirport");
    }
    airGate(id) {
        return this.node(id);
    }
    get airGates() {
        return this.nodes.filter((a) => a.type === "AirGate");
    }
    airAirline(id) {
        return this.node(id);
    }
    get airAirlines() {
        return this.nodes.filter((a) => a.type === "AirAirline");
    }
    railCompany(id) {
        return this.node(id);
    }
    get railCompanies() {
        return this.nodes.filter((a) => a.type === "RailCompany");
    }
    railLine(id) {
        return this.node(id);
    }
    get railLines() {
        return this.nodes.filter((a) => a.type === "RailLine");
    }
    railStation(id) {
        return this.node(id);
    }
    get railStations() {
        return this.nodes.filter((a) => a.type === "RailStation");
    }
    seaCompany(id) {
        return this.node(id);
    }
    get seaCompanies() {
        return this.nodes.filter((a) => a.type === "SeaCompany");
    }
    seaLine(id) {
        return this.node(id);
    }
    get seaLines() {
        return this.nodes.filter((a) => a.type === "SeaLine");
    }
    seaStop(id) {
        return this.node(id);
    }
    get seaStops() {
        return this.nodes.filter((a) => a.type === "SeaStop");
    }
    busCompany(id) {
        return this.node(id);
    }
    get busCompanies() {
        return this.nodes.filter((a) => a.type === "BusCompany");
    }
    busLine(id) {
        return this.node(id);
    }
    get busLines() {
        return this.nodes.filter((a) => a.type === "BusLine");
    }
    busStop(id) {
        return this.node(id);
    }
    get busStops() {
        return this.nodes.filter((a) => a.type === "BusStop");
    }
}
//# sourceMappingURL=lib.js.map