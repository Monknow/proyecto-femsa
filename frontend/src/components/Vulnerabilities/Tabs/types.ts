import type {Tab} from "@/types/tabs";
import type {Dispatch, SetStateAction} from "react";

export type TabsProps = {
    currenTab: Tab;
    setCurrentTab: Dispatch<SetStateAction<Tab>>;
};
