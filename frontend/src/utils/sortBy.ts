import type {SortedBy} from "@/types/sorting";

type Row = Record<string, string | number>;

export const sortBy = <T extends object>(data: T[], sortedBy?: SortedBy): T[] => {
    if (!sortedBy) {
        return data;
    }

    const get = (item: T) => (item as Row)[sortedBy.propertyName];

    const orderFactor = sortedBy.order === "ascending" ? 1 : -1;

    if (typeof get(data[0]) === "number") {
        console.log("is a number");
        return data.toSorted((a, b) => orderFactor * (Number(get(a)) - Number(get(b))));
    }

    return data.toSorted((a, b) => {
        const aValue = get(a) as string;
        const bValue = get(b) as string;

        if (aValue < bValue) return -orderFactor;
        if (aValue > bValue) return orderFactor;
        return 0;
    });
};
