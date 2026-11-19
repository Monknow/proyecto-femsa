import {SingleBreakdown} from "@components/SingleBreakdown";
import {WidgetWrapper} from "@components/WidgetWrapper";
import {Async} from "@/components/Async";
import {api, type Aggregation} from "@/api/client";
import {useApi} from "@/hooks/useApi";

import classes from "./styles.module.css";

const toItems = (aggregation: Aggregation) =>
    Object.entries(aggregation).map(([name, value]) => ({name: name.toLowerCase().replaceAll("_", " "), value}));

export const UsefulBreakdowns = () => {
    const severity = useApi(() => api.aggregateVulnerabilities("severity"));
    const status = useApi(() => api.aggregateVulnerabilities("finding_status"));
    const exposure = useApi(() => api.aggregateServers("exposure_category"));

    return (
        <WidgetWrapper title="Estadisticas" className={classes["useful-breakdowns"]}>
            <Async state={severity}>
                {(data) => (
                    <SingleBreakdown
                        title="Gravedad"
                        data={Object.entries(data)
                            .map(([level, value]) => ({name: `nivel ${level}`, value, level: Number(level)}))
                            .sort((a, b) => a.level - b.level)}
                    />
                )}
            </Async>
            <Async state={status}>{(data) => <SingleBreakdown title="Status" data={toItems(data)} />}</Async>
            <Async state={exposure}>{(data) => <SingleBreakdown title="Exposición" data={toItems(data)} />}</Async>
        </WidgetWrapper>
    );
};
