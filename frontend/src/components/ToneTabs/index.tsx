import type {Dispatch, SetStateAction} from "react";

import {toneFor} from "@/components/Badge";
import classes from "./styles.module.css";
import {cn} from "@/utils/cn";

type ToneTabsProps<T extends string> = {
    tabs: Record<T, string>;
    current: T;
    setCurrent: Dispatch<SetStateAction<T>>;
};

/** Filter tabs styled like the status badges in the tables (tone comes from the tab key). */
export const ToneTabs = <T extends string>({tabs, current, setCurrent}: ToneTabsProps<T>) => (
    <ul className={cn(classes["tabs"], "box-shadow")}>
        {(Object.keys(tabs) as T[]).map((tab) => (
            <li key={tab}>
                <button
                    type="button"
                    aria-pressed={current === tab}
                    onClick={() => setCurrent(tab)}
                    className={`${classes[toneFor(tab)]} ${current === tab ? classes["active"] : ""}`}>
                    {tabs[tab]}
                </button>
            </li>
        ))}
    </ul>
);
