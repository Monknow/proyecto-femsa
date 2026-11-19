import {useMemo, useState, type FC} from "react";

import {sortBy} from "@/utils/sortBy";
import type {SortedBy} from "@/types/sorting";

import classes from "./styles.module.css";
import {HeaderCell} from "./HeaderCell";
import type {TableProps} from "./types";

export const Table: FC<TableProps> = ({data, idColumn}) => {
    const [sortedBy, setSortedBy] = useState<SortedBy>();

    const columns = Object.keys(data[0] ?? {});

    const sortedData = useMemo(() => sortBy(data, sortedBy), [sortedBy, data]);

    return (
        <div className={classes["wrapper"]}>
            <table className={classes["table"]}>
                <thead>
                    <tr>
                        {columns.map((columnName) => {
                            return (
                                <HeaderCell
                                    key={columnName}
                                    name={columnName}
                                    sortedBy={sortedBy}
                                    setSortedBy={setSortedBy}
                                />
                            );
                        })}
                    </tr>
                </thead>
                <tbody>
                    {sortedData.map((vuln) => {
                        return (
                            <tr key={String(vuln[idColumn])}>
                                {Object.entries(vuln).map(([column, value]) => {
                                    return <td key={column}>{value === null ? "" : String(value)}</td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};
