import type {TableRow} from "@/types/data";
import type {Filter} from "@/types/filtering";

export type ExplorerProps = {
    title: string;
    fetcher: () => Promise<TableRow[]>;
    initialFilters?: Filter[];
};
