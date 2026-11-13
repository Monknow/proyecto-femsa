import {SingleBreakdown} from "@components/SingleBreakdown";
import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

const MOCK_DATA_1 = [
    {name: "very low", value: 5, level: 1},
    {name: "low", value: 15, level: 2},
    {name: "medium", value: 10, level: 3},
    {name: "high", value: 20, level: 4},
    {name: "very high", value: 50, level: 5},
];

const MOCK_DATA_2 = [
    {name: "new", value: 50},
    {name: "active", value: 20},
    {name: "remediated", value: 10},
    {name: "reopened", value: 15},
];

const MOCK_DATA_3 = [
    {name: "internal", value: 50},
    {name: "internet exposed", value: 20},
];

export const UsefulBreakdowns = () => {
    return (
        <WidgetWrapper title="Estadisticas" className={classes["useful-breakdowns"]}>
            <SingleBreakdown title="Gravedad" data={MOCK_DATA_1} />
            <SingleBreakdown title="Status" data={MOCK_DATA_2} />
            <SingleBreakdown title="Exposición" data={MOCK_DATA_3} />
        </WidgetWrapper>
    );
};
