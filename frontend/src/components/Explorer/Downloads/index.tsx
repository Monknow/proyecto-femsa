import type {FC} from "react";

import {exportData, type ExportFormat} from "@/utils/exportData";

import classes from "./styles.module.css";
import type {DownloadsProps} from "./types";

const FORMATS: {format: ExportFormat; label: string}[] = [
    {format: "pdf", label: "PDF"},
    {format: "csv", label: "CSV"},
    {format: "excel", label: "Excel"},
    {format: "json", label: "JSON"},
];

export const Downloads: FC<DownloadsProps> = ({data}) => {
    return (
        <section className={classes["downloads"]}>
            <p>Descargar como:</p>
            <ul>
                {FORMATS.map(({format, label}) => (
                    <li key={format}>
                        <button type="button" disabled={data.length === 0} onClick={() => exportData(data, format)}>
                            {label}
                        </button>
                    </li>
                ))}
            </ul>
        </section>
    );
};
