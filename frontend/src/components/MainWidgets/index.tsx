import {UsefulBreakdowns} from "@components/UsefulBreakdowns";
import {WidgetNumber} from "@components/WidgetNumber";
import {WidgetWrapper} from "@components/WidgetWrapper";
import {MapChart} from "@components/MapChart";
import {BackLog} from "@components/BackLog";
import {TopServers} from "@components/TopServers";

import classes from "./styles.module.css";

export const MainWidgets = () => {
    return (
        <main className={classes["main-widgets"]}>
            <WidgetNumber title="Vulnerabilidades" number={923} label="Activas" />
            <UsefulBreakdowns />
            <WidgetWrapper title="Mapa">
                <MapChart />
            </WidgetWrapper>
            <BackLog />
            <TopServers />
        </main>
    );
};
