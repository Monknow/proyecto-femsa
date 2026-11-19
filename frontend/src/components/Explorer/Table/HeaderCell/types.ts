import type {SortedBy} from "@/types/sorting";
import type {Dispatch, SetStateAction} from "react";

export type HeaderCellProps = {
    name: string;
    sortedBy: SortedBy | undefined;
    setSortedBy: Dispatch<SetStateAction<SortedBy | undefined>>;
};
