import type {Dispatch, SetStateAction} from "react";

import type {TableRow} from "@/types/data";
import type {Filter} from "@/types/filtering";

export type FiltersProps = {
    data: TableRow[];
    filters: Filter[];
    setFilters: Dispatch<SetStateAction<Filter[]>>;
};
