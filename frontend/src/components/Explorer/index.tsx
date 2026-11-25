import {useState, type FC} from "react";

import {Table} from "@components/Explorer/Table";
import {Filters} from "@components/Explorer/Filters";
import {Downloads} from "@components/Explorer/Downloads";

import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";
import type {Filter} from "@/types/filtering";
import type {TableRow} from "@/types/data";

import classes from "./styles.module.css";
import type {ExplorerProps} from "./types";
import {getFilter} from "@/utils/filters";

export const Explorer: FC<ExplorerProps> = ({title, fetcher, initialFilters = []}) => {
    const source = useApi<TableRow[]>(fetcher);
    const [filters, setFilters] = useState<Filter[]>(initialFilters);

    return (
        <div className={classes["explorer"]}>
            <header>
                <h1>{title}</h1>
            </header>
            <Async state={source}>
                {(data) => {
                    const filteredData = data.filter((entry) => {
                        return filters.every(({columnName, type, comparable}) => {
                            return getFilter(entry[columnName], type, comparable);
                        });
                    });

                    return (
                        <>
                            <Downloads data={filteredData} />
                            <Filters data={data} filters={filters} setFilters={setFilters} />
                            <Table data={filteredData} idColumn="_id" />
                        </>
                    );
                }}
            </Async>
        </div>
    );
};
