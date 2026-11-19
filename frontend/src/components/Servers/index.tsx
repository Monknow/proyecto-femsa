import {useState} from "react";

import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";

import classes from "./styles.module.css";
import {Server} from "@/components/Servers/Server";
import {Tabs} from "./Tabs";
import type {ServerTab} from "@/types/serverTabs";

export const Servers = () => {
    const [currenTab, setCurrenTab] = useState<ServerTab>("all");
    const servers = useApi(api.getServers);

    return (
        <div className={classes["servers"]}>
            <h1>Servers</h1>

            <Tabs currenTab={currenTab} setCurrentTab={setCurrenTab} />

            <Async state={servers}>
                {(data) => {
                    const filteredServers =
                        currenTab === "all" ? data : data.filter((entry) => entry.risk_band?.toLowerCase() === currenTab);

                    return (
                        <ul className={classes["list"]}>
                            {filteredServers.map((server) => {
                                return <Server server={server} key={server._id} />;
                            })}
                        </ul>
                    );
                }}
            </Async>
        </div>
    );
};
