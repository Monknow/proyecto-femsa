import type {TableRow} from "@/types/data";
import type {Filter} from "@/types/filtering";

export type SingleFilterProps = {
    data: TableRow[];
    columnName: string;
    onAdd: (filter: Filter) => void;
};
