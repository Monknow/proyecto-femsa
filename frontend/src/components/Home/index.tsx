import {UsefulBreakdowns} from "@components/UsefulBreakdowns";
import {WidgetNumber} from "@components/WidgetNumber";
import {MapChart} from "@components/MapChart";
import {BackLog} from "@components/BackLog";
import {TopServers} from "@components/TopServers";

import {Async} from "@/components/Async";
import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import {HotBar} from "@components/Home/HotBar";

import classes from "./styles.module.css";

export const Home = () => {
    const statuses = useApi(() => api.aggregateVulnerabilities("finding_status"));

    return (
        <div className={classes["home"]}>
            <h1>Inicio</h1>
            <HotBar />
            <Async
                state={statuses}
                skeleton={<WidgetNumber className={classes["active"]} title="Vulnerabilidades" loading />}>
                {(counts) => (
                    <WidgetNumber
                        className={classes["active"]}
                        title="Vulnerabilidades"
                        number={counts["ACTIVE"] ?? 0}
                        label="Activas"
                    />
                )}
            </Async>
            <UsefulBreakdowns className={classes["stats"]} />
            <MapChart className={classes["map"]} />
            <BackLog className={classes["backlog"]} />
            <TopServers className={classes["servers"]} />
        </div>
    );
};
