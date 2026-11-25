import {api} from "@/api/client";
import {DataList} from "@/components/DataList";
import {Server} from "@/components/Servers/Server";

import type {ServerTab} from "@/types/serverTabs";

const tabs: Record<ServerTab, string> = {
    all: "Todos",
    very_high: "Muy alto",
    high: "Alto",
    medium: "Medio",
    low: "Bajo",
};

export const Servers = () => (
    <DataList
        title="Servidores"
        fetcher={api.getServers}
        tabs={tabs}
        tabValue={(server) => server.risk_band}
        headers={["Riesgo", "Ambiente", "Criticidad", "Vulnerabilidades"]}
        renderRow={(server) => <Server server={server} key={server._id} />}
    />
);
