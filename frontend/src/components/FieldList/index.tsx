import type {FC} from "react";

import {humanize} from "@/components/Badge";
import classes from "./styles.module.css";

export const formatValue = (value: unknown): string => {
    if (value === null || value === undefined || value === "") return "—";
    if (typeof value === "boolean") return value ? "Sí" : "No";
    if (typeof value === "string") return humanize(value);
    return String(value);
};

type FieldListProps = {
    items: [label: string, value: unknown][];
};

export const FieldList: FC<FieldListProps> = ({items}) => (
    <dl className={classes["fields"]}>
        {items.map(([label, value]) => (
            <div key={label} className={classes["field"]}>
                <dt>{label}</dt>
                <dd>{formatValue(value)}</dd>
            </div>
        ))}
    </dl>
);
