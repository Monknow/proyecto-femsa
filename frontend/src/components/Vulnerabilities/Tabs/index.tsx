import {type FC} from "react";
import classes from "./styles.module.css";
import type {TabsProps} from "./types";
import type {Tab} from "@/types/tabs";

const tabs: Record<Tab, string> = {
    all: "All",
    active: "Active",
    new: "New",
    reopened: "Reopened",
    remediated: "Remediated",
};

export const Tabs: FC<TabsProps> = ({currenTab, setCurrentTab}) => {
    return (
        <ul className={classes["tabs"]}>
            {(Object.keys(tabs) as Tab[]).map((tab) => {
                return (
                    <li
                        key={tab}
                        onClick={() => {
                            setCurrentTab(tab);
                        }}
                        className={currenTab === tab ? classes["active"] : "not-active"}>
                        {tabs[tab]}
                    </li>
                );
            })}
        </ul>
    );
};
