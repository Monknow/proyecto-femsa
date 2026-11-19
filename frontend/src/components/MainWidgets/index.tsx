import {UsefulBreakdowns} from "@components/UsefulBreakdowns";
import {WidgetNumber} from "@components/WidgetNumber";
import {WidgetWrapper} from "@components/WidgetWrapper";
import {MapChart} from "@components/MapChart";
import {BackLog} from "@components/BackLog";
import {TopServers} from "@components/TopServers";

import {Async} from "@/components/Async";
import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";

import classes from "./styles.module.css";

export const MainWidgets = () => {
    const statuses = useApi(() => api.aggregateVulnerabilities("finding_status"));

    return (
        <main className={classes["main-widgets"]}>
            <Async state={statuses}>
                {(counts) => <WidgetNumber title="Vulnerabilidades" number={counts["ACTIVE"] ?? 0} label="Activas" />}
            </Async>
            <UsefulBreakdowns />
            <WidgetWrapper title="Mapa">
                <MapChart />
            </WidgetWrapper>
            <BackLog />
            <TopServers />
        </main>
    );
};
