import {useState, type CSSProperties, type FC, type ReactNode} from "react";
import {Link} from "react-router";

import DangerIcon from "@assets/svg/danger.svg?react";
import OpenIcon from "@assets/svg/open.svg?react";
import ArrowDownIcon from "@assets/svg/arrow_down.svg?react";

import {humanize, type Tone} from "@/components/Badge";
import {FieldList} from "@/components/FieldList";
import classes from "./styles.module.css";

type DataRowProps = {
    title: string;
    tone?: Tone;
    cells: ReactNode[];
    href?: string;
    /** When omitted the row is not expandable. */
    details?: object;
    actions?: ReactNode;
    icon?: ReactNode;
    /** Width of the trailing actions column; must match the header. */
    actionsWidth?: string;
};

export const DataRowHeader: FC<{labels: string[]; titleLabel?: string; actionsWidth?: string}> = ({
    labels,
    titleLabel = "ID",
    actionsWidth,
}) => (
    <li
        className={`${classes["row-header"]} ${classes["grid"]}`}
        style={{"--cells": labels.length, ...(actionsWidth && {"--actions": actionsWidth})} as CSSProperties}>
        <span />
        <span>{titleLabel}</span>
        {labels.map((label) => (
            <span key={label}>{label}</span>
        ))}
        <span />
    </li>
);

export const DataRow: FC<DataRowProps> = ({title, tone = "neutral", cells, href, details, actions, icon, actionsWidth}) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <li className={`${classes["row"]} ${isOpen ? classes["open"] : ""}`}>
            <div
                className={classes["grid"]}
                style={{"--cells": cells.length, ...(actionsWidth && {"--actions": actionsWidth})} as CSSProperties}>
                <span className={`${classes["icon"]} ${classes[tone]}`}>
                    {icon ?? <DangerIcon />}
                </span>
                <span className={classes["title"]} title={title}>
                    {title}
                </span>
                {cells.map((cell, index) => (
                    <span key={index} className={classes["cell"]}>
                        {cell}
                    </span>
                ))}
                <span className={classes["actions"]}>
                    {actions}
                    {href && (
                        <Link to={href} title="Abrir por separado" aria-label="Abrir por separado">
                            <OpenIcon />
                        </Link>
                    )}
                    {details && (
                        <button
                            type="button"
                            aria-label={isOpen ? "Ocultar detalles" : "Mostrar detalles"}
                            aria-expanded={isOpen}
                            onClick={() => setIsOpen(!isOpen)}>
                            <ArrowDownIcon />
                        </button>
                    )}
                </span>
            </div>

            {details && isOpen && (
                <div className={classes["details"]}>
                    <FieldList
                        items={Object.entries(details)
                            .filter(([key]) => key !== "_id")
                            .map(([key, value]) => [humanize(key), value])}
                    />
                </div>
            )}
        </li>
    );
};
