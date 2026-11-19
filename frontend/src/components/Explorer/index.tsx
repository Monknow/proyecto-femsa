import {useState} from "react";

import {Table} from "@components/Explorer/Table";
import {Filters} from "@components/Explorer/Filters";
import {Downloads} from "@components/Explorer/Downloads";

import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";
import type {Filter} from "@/types/filtering";
import type {TableRow} from "@/types/data";

import classes from "./styles.module.css";
import {getFilter} from "@/utils/filters";

export const Explorer = () => {
    const vulnerabilities = useApi(api.getVulnerabilities);
    const [filters, setFilters] = useState<Filter[]>([
        {columnName: "severity", type: "greater or equal", comparable: 3},
        {columnName: "finding_status", type: "is not", comparable: "REMEDIATED"},
        // {columnName: "exploitability", type: "is", comparable: "High"},
    ]);

    return (
        <div className={classes["explorer"]}>
            <header>
                <h1>Explorador de Datos</h1>
            </header>
            <Async state={vulnerabilities}>
                {(vulns) => {
                    const data: TableRow[] = vulns;
                    const filteredData = data.filter((entry) => {
                        return filters.every(({columnName, type, comparable}) => {
                            return getFilter(entry[columnName], type, comparable);
                        });
                    });

                    return (
                        <>
                            <Filters data={data} filters={filters} setFilters={setFilters} />
                            <Table data={filteredData} idColumn="_id" />
                        </>
                    );
                }}
            </Async>
            <Downloads />
        </div>
    );
};
