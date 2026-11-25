import {Explorer} from "@/components/Explorer";
import {api} from "@/api/client";

const ExplorerServersPage = () => {
    return <Explorer title="Explorador de Datos: Servidores" fetcher={api.getServers} />;
};

export default ExplorerServersPage;
