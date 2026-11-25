import {Explorer} from "@/components/Explorer";
import {api} from "@/api/client";
import type {Filter} from "@/types/filtering";

const initialFilters: Filter[] = [
    {columnName: "severity", type: "greater or equal", comparable: 3},
    {columnName: "finding_status", type: "is not", comparable: "REMEDIATED"},
];

const ExplorerPage = () => {
    return (
        <Explorer title="Explorador de Datos: Vulnerabilidades" fetcher={api.getVulnerabilities} initialFilters={initialFilters} />
    );
};

export default ExplorerPage;
