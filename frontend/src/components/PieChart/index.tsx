import {PieChart as RechartPieChart, Pie, Tooltip, Legend} from "recharts";

import {type Props} from "./types";

export const PieChart = ({data, dataKey, nameKey}: Props) => {
    return (
        <RechartPieChart
            style={{width: "100%", height: "100%", maxWidth: "400px", maxHeight: "400px", aspectRatio: 1}}
            responsive>
            <Pie data={data} dataKey={dataKey} nameKey={nameKey} stroke="black" label />
            <Tooltip />
            <Legend />
        </RechartPieChart>
    );
};
