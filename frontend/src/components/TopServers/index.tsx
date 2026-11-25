import {WidgetList} from "../WidgetList";
import {Async} from "@/components/Async";
import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import type {FC} from "react";
import type {TopServerProps} from "./types";

const TOP = 5;

export const TopServers: FC<TopServerProps> = ({className}) => {
    // Number of vulnerabilities per server
    const perServer = useApi(() => api.aggregateVulnerabilities("server_id"));

    return (
        <Async
            state={perServer}
            skeleton={<WidgetList className={className} title="Top Servidores" label="vulnerabilidades" loading />}>
            {(counts) => {
                const list = Object.entries(counts)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, TOP)
                    .map(([name, value]) => ({name, value, link: `/servers/${name}`}));

                return <WidgetList className={className} title="Top Servidores" list={list} label="vulnerabilidades" />;
            }}
        </Async>
    );
};
