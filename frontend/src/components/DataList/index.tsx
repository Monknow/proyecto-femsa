import {useState, type ReactNode} from "react";

import {useApi} from "@/hooks/useApi";
import {Async} from "@/components/Async";
import {DataRowHeader} from "@/components/DataRow";
import {ToneTabs} from "@/components/ToneTabs";

import classes from "./styles.module.css";

type DataListProps<Item extends {_id: string}, Tab extends string> = {
    title: string;
    fetcher: () => Promise<Item[]>;
    /** Tab key -> label. Must include "all". */
    tabs: Record<Tab, string>;
    /** Value of the item that is matched against the selected tab. */
    tabValue: (item: Item) => string | null | undefined;
    headers: string[];
    renderRow: (item: Item) => ReactNode;
};

/** Titled, tab-filtered list of expandable rows. Pages only supply their data and row. */
export const DataList = <Item extends {_id: string}, Tab extends string>({
    title,
    fetcher,
    tabs,
    tabValue,
    headers,
    renderRow,
}: DataListProps<Item, Tab>) => {
    const [currentTab, setCurrentTab] = useState<Tab>("all" as Tab);
    const items = useApi(fetcher);

    return (
        <div className={classes["data-list"]}>
            <h1>{title}</h1>

            <ToneTabs tabs={tabs} current={currentTab} setCurrent={setCurrentTab} />

            <Async state={items}>
                {(data) => {
                    const filtered =
                        currentTab === "all" ? data : data.filter((item) => tabValue(item)?.toLowerCase() === currentTab);

                    return (
                        <ul className={classes["list"]}>
                            <DataRowHeader labels={headers} />
                            {filtered.map(renderRow)}
                        </ul>
                    );
                }}
            </Async>
        </div>
    );
};
