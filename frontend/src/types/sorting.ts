export type SortOrder = "ascending" | "descending";

export interface SortedBy {
    propertyName: string;
    order: SortOrder;
}
