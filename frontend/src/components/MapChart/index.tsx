import Plot from "react-plotly.js";

import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";
import {Skeleton} from "../Skeleton";
import {WidgetWrapper} from "../WidgetWrapper";
import type {FC} from "react";
import type {MapChartProps} from "./types";
import {cn} from "@utils/cn";

import classes from "./styles.module.css";

// Countries (ISO-3 codes) grouped into the three regions shown on the map.
// The Caribbean is grouped with North America.
const regions = [
    {
        name: "Norteamérica",
        group: "REGION_NORTH",
        countries: [
            "USA",
            "CAN",
            "MEX",
            "GRL",
            "BHS",
            "CUB",
            "JAM",
            "HTI",
            "DOM",
            "PRI",
            "TTO",
            "BRB",
            "ATG",
            "DMA",
            "GRD",
            "KNA",
            "LCA",
            "VCT",
        ],
    },
    {
        name: "Centroamérica",
        group: "REGION_CENTRAL",
        countries: ["GTM", "BLZ", "SLV", "HND", "NIC", "CRI", "PAN"],
    },
    {
        name: "Sudamérica",
        group: "REGION_SOUTH",
        countries: ["COL", "VEN", "GUY", "SUR", "ECU", "PER", "BRA", "BOL", "PRY", "CHL", "ARG", "URY"],
    },
];

// Open (not remediated) vulnerabilities per server region_group.
const countByRegionGroup = async (): Promise<Record<string, number>> => {
    const [vulns, servers] = await Promise.all([api.getVulnerabilities(), api.getServers()]);
    const groupByServer = new Map(servers.map((server) => [server._id, server.region_group ?? ""]));

    const counts: Record<string, number> = {};
    for (const vuln of vulns) {
        if (vuln.finding_status === "REMEDIATED") continue;
        const group = groupByServer.get(vuln.server_id);
        if (group) counts[group] = (counts[group] ?? 0) + 1;
    }
    return counts;
};

export const MapChart: FC<MapChartProps> = ({className}) => {
    const counts = useApi(countByRegionGroup);

    return (
        <Async
            state={counts}
            skeleton={
                <WidgetWrapper title="Mapa" className={cn(classes["map"], className)}>
                    <div className={classes["skeleton"]}>
                        <Skeleton circle width="min(100%, 60vh)" height="100%" />
                    </div>
                </WidgetWrapper>
            }>
            {(data) => <RegionMap className={className} counts={data} />}
        </Async>
    );
};

const RegionMap = ({counts, className}: {counts: Record<string, number>; className?: string}) => {
    const rows = regions.flatMap(({name, group, countries}) =>
        countries.map((country) => ({location: country, region: name, value: counts[group] ?? 0})),
    );

    const data = [
        {
            type: "choropleth",
            locationmode: "ISO-3",
            locations: rows.map((row) => row.location),
            z: rows.map((row) => row.value),
            text: rows.map((row) => row.region),
            hovertemplate: "%{text}: %{z} vulnerabilidades<extra></extra>",
            colorscale: "Reds",
            zmin: 0,
            colorbar: {title: {text: "Vulnerabilidades"}},
        },
    ];

    const layout = {
        autosize: true,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        geo: {
            bgcolor: "rgba(0,0,0,0)",
            scope: "world",
            showcountries: true, // Country borders
            projection: {
                type: "orthographic",
                rotation: {lon: -80, lat: 10},
            },
        },
        margin: {t: 0, b: 0, l: 0, r: 0},
    };

    const config = {
        displayModeBar: false, // Hides the entire modebar toolbar
    };

    return (
        <WidgetWrapper title="Mapa" className={cn(classes["map"], className)}>
            <Plot
                className={classes["plot"]}
                style={{width: "100%", height: "100%", background: "transparent"}}
                layout={layout}
                data={data}
                config={config}
                useResizeHandler={true}
            />
        </WidgetWrapper>
    );
};
