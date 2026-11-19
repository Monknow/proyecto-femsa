import {type FC} from "react";
import classes from "./styles.module.css";
import type {TabsProps} from "./types";
import type {ServerTab} from "@/types/serverTabs";

const tabs: Record<ServerTab, string> = {
    all: "All",
    very_high: "Very High",
    high: "High",
    medium: "Medium",
    low: "Low",
};

export const Tabs: FC<TabsProps> = ({currenTab, setCurrentTab}) => {
    return (
        <ul className={classes["tabs"]}>
            {(Object.keys(tabs) as ServerTab[]).map((tab) => {
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
