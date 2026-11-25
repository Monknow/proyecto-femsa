export type WidgetListProps = {
    title: string;
    label: string;
    list?: {name: string; value: number; link?: string}[];
    loading?: boolean;
    className?: string;
};
