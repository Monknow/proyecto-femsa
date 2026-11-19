import type {ServerTab} from "@/types/serverTabs";
import type {Dispatch, SetStateAction} from "react";

export type TabsProps = {
    currenTab: ServerTab;
    setCurrentTab: Dispatch<SetStateAction<ServerTab>>;
};
