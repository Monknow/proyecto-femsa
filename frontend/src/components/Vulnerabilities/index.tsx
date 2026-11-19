import {useState} from "react";

import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";

import classes from "./styles.module.css";
import {Vulnerability} from "@/components/Vulnerabilities/Vulnerability";
import {Tabs} from "./Tabs";
import type {Tab} from "@/types/tabs";

export const Vulnerabilities = () => {
    const [currenTab, setCurrenTab] = useState<Tab>("all");
    const vulnerabilities = useApi(api.getVulnerabilities);

    return (
        <div className={classes["vulnerabilities"]}>
            <h1>Vulnerabilities</h1>

            <Tabs currenTab={currenTab} setCurrentTab={setCurrenTab} />

            <Async state={vulnerabilities}>
                {(vulns) => {
                    const filteredVulns =
                        currenTab === "all"
                            ? vulns
                            : vulns.filter((entry) => entry.finding_status?.toLowerCase() === currenTab);

                    return (
                        <ul className={classes["list"]}>
                            {filteredVulns.map((vuln) => {
                                return <Vulnerability vuln={vuln} key={vuln._id} />;
                            })}
                        </ul>
                    );
                }}
            </Async>
        </div>
    );
};
