import type {FC} from "react";

import {cn} from "@/utils/cn";

import {SingleBreakdown} from "@components/SingleBreakdown";
import {WidgetWrapper} from "@components/WidgetWrapper";
import {Async} from "@/components/Async";
import {api, type Aggregation} from "@/api/client";
import {useApi} from "@/hooks/useApi";

import classes from "./styles.module.css";
import type {UsefulBreakdownsProps} from "./types";

const toItems = (aggregation: Aggregation) =>
    Object.entries(aggregation).map(([name, value]) => ({name: name.toLowerCase().replaceAll("_", " "), value}));

// Colors follow the meaning of each value: green = good, amber/orange = needs attention, red = bad.
const STATUS_PALETTE = {
    remediated: "var(--color-emerald)",
    new: "var(--color-amber)",
    reopened: "var(--color-red)",
};

const EXPOSURE_PALETTE = {
    internal: "var(--color-emerald)",
    "internet exposed": "var(--color-red)",
};

export const UsefulBreakdowns: FC<UsefulBreakdownsProps> = ({className}) => {
    const severity = useApi(() => api.aggregateVulnerabilities("severity"));
    const status = useApi(() => api.aggregateVulnerabilities("finding_status"));
    const exposure = useApi(() => api.aggregateServers("exposure_category"));

    return (
        <WidgetWrapper title="Estadisticas" className={cn(classes["useful-breakdowns"], className)}>
            <Async state={severity} skeleton={<SingleBreakdown title="Gravedad" loading />}>
                {(data) => (
                    <SingleBreakdown
                        title="Gravedad"
                        data={Object.entries(data)
                            .map(([level, value]) => ({name: `nivel ${level}`, value, level: Number(level)}))
                            .sort((a, b) => a.level - b.level)}
                    />
                )}
            </Async>
            <Async state={status} skeleton={<SingleBreakdown title="Estatus" loading />}>{(data) => <SingleBreakdown title="Estatus" data={toItems(data)} palette={STATUS_PALETTE} />}</Async>
            <Async state={exposure} skeleton={<SingleBreakdown title="Exposición" loading />}>{(data) => <SingleBreakdown title="Exposición" data={toItems(data)} palette={EXPOSURE_PALETTE} />}</Async>
        </WidgetWrapper>
    );
};
