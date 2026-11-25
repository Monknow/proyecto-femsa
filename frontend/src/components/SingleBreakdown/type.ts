export type DataItem = {name: string; value: number; level?: number};

export type SingleBreakdownProps = {
    title: string;
    data?: DataItem[];
    loading?: boolean;
    /** Maps a (normalized, lowercase) item name to a CSS color. Unmapped items fall back to the default palette. */
    palette?: Record<string, string>;
};
