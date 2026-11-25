import type {FC, ReactNode} from "react";

import classes from "./styles.module.css";

export type Tone = "danger" | "warning" | "ok" | "neutral";

const toneByValue: Record<string, Tone> = {
    very_high: "danger",
    high: "danger",
    critical: "danger",
    active: "danger",
    reopened: "danger",
    medium: "warning",
    new: "warning",
    low: "ok",
    remediated: "ok",
};

export const toneFor = (value?: string | null): Tone => toneByValue[value?.toLowerCase() ?? ""] ?? "neutral";

export const humanize = (value: string) => {
    const text = value.replace(/_/g, " ").trim();
    return text.charAt(0).toUpperCase() + text.slice(1);
};

export const Badge: FC<{tone?: Tone; children: ReactNode}> = ({tone = "neutral", children}) => (
    <span className={`${classes["badge"]} ${classes[tone]}`}>{children}</span>
);
