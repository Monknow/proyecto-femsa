import Plot from "react-plotly.js";

const alcoholData = [
    {location: "United States", alcohol: 9.2},
    {location: "Canada", alcohol: 10.2},
    {location: "Brazil", alcohol: 8.8},
    {location: "Argentina", alcohol: 9.3},
    {location: "Mexico", alcohol: 7.2},
];

export const MapChart = () => {
    const unpack = (rows: any[], key: string) => rows.map((row) => row[key]);

    const data = [
        {
            type: "choropleth",
            locationmode: "country names",
            locations: unpack(alcoholData, "location"),
            z: unpack(alcoholData, "alcohol"),
            text: unpack(alcoholData, "location"),
            autocolorscale: true,
        },
    ];

    const layout = {
        autosize: true,
        geo: {
            scope: "world",
            showcountries: true, // Country borders
            projection: {
                type: "orthographic",
            },
        },
        margin: {t: 0, b: 0, l: 0, r: 0},
    };

    const config = {
        displayModeBar: false, // Hides the entire modebar toolbar
    };

    return <Plot layout={layout} data={data} config={config} useResizeHandler={true} />;
};
