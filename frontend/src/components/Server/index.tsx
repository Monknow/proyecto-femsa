import {useParams} from "react-router";

import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";

import classes from "./styles.module.css";
import {Status} from "@/components/ServerWidgets/Status";
import {Diagnosis} from "@/components/ServerWidgets/Diagnosis";
import {Score} from "@/components/ServerWidgets/Score";
import {Infrastructure} from "@/components/ServerWidgets/Infrastructure";
import {Details} from "@/components/ServerWidgets/Details";
import {History} from "@/components/ServerWidgets/History";

export const Server = () => {
    const params = useParams();
    const id = params.id ?? "";
    const server = useApi(() => api.getServer(id), [id]);

    return (
        <main className={classes["server-widgets"]}>
            <header className={classes["header"]}>
                <h1>Servidor #{id}</h1>
            </header>
            <Async state={server}>
                {(data) => (
                    <>
                    <Status environment={data.environment} lifecycle={data.os_lifecycle} />
                    <Diagnosis exposure={data.exposure_category} />
                    <Score
                        riskBand={data.risk_band}
                        vulnerabilityVolume={data.vulnerability_volume_band}
                        assetCriticality={data.asset_criticality}
                        inventoryFreshness={data.inventory_freshness_band}
                    />
                    <Infrastructure
                        id={data._id}
                        infrastructure={data.infrastructure_type}
                        cpu={data.cpu_capacity_band}
                        memory={data.memory_capacity_band}
                        architecture={data.architecture_band}
                    />
                    <Details
                        osFamily={data.os_family}
                        assetType={data.asset_type}
                        role={data.functional_role}
                        region={data.region_group}
                        bootAge={data.boot_age_band}
                    />
                    <History id={id} />
                    </>
                )}
            </Async>
        </main>
    );
};
