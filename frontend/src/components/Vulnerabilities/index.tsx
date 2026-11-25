import {api} from "@/api/client";
import {DataList} from "@/components/DataList";
import {Vulnerability} from "@/components/Vulnerabilities/Vulnerability";

import type {Tab} from "@/types/tabs";

const tabs: Record<Tab, string> = {
    all: "Todas",
    active: "Activas",
    new: "Nuevas",
    reopened: "Reabiertas",
    remediated: "Remediadas",
};

export const Vulnerabilities = () => (
    <DataList
        title="Vulnerabilidades"
        fetcher={api.getVulnerabilities}
        tabs={tabs}
        tabValue={(vuln) => vuln.finding_status}
        headers={["Puntaje", "Estatus", "Severidad", "Servidor"]}
        renderRow={(vuln) => <Vulnerability vuln={vuln} key={vuln._id} />}
    />
);
