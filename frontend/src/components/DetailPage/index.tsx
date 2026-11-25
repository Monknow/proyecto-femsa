import type {FC, ReactNode} from "react";
import {Link} from "react-router";

import {toneFor, type Tone} from "@/components/Badge";
import {formatValue} from "@/components/FieldList";
import classes from "./styles.module.css";

type DetailPageProps = {
    title: string;
    backTo: string;
    backLabel: string;
    children: ReactNode;
};

export const DetailPage: FC<DetailPageProps> = ({title, backTo, backLabel, children}) => (
    <main className={classes["page"]}>
        <header className={classes["header"]}>
            <Link to={backTo} className={classes["back"]}>
                ← {backLabel}
            </Link>
            <h1>{title}</h1>
        </header>
        <div className={classes["grid"]}>{children}</div>
    </main>
);

/** Large highlighted value for summary widgets. Tone defaults to the value's own risk/status tone. */
export const BigValue: FC<{value: unknown; tone?: Tone}> = ({value, tone}) => {
    const resolved = tone ?? (typeof value === "string" ? toneFor(value) : "neutral");
    return <strong className={`${classes["big-value"]} ${classes[resolved]}`}>{formatValue(value)}</strong>;
};

type TimelineItem = {_id: string; file_name: string; upload_date: string};

export const Timeline: FC<{items: TimelineItem[]}> = ({items}) => {
    if (items.length === 0) return <p className={classes["empty"]}>Sin historial</p>;

    return (
        <ul className={classes["timeline"]}>
            {items.map(({_id, file_name, upload_date}) => (
                <li key={_id}>
                    <span className={classes["dot"]} />
                    <div className={classes["entry"]}>
                        <p>Actualizado</p>
                        <small>{file_name}</small>
                    </div>
                    <time>{new Date(upload_date).toLocaleDateString()}</time>
                </li>
            ))}
        </ul>
    );
};
