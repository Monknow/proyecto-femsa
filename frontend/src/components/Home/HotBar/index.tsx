import {useState} from "react";

import {api, type ReportType} from "@/api/client";

import DownloadIcon from "@assets/svg/download.svg?react";

import classes from "./styles.module.css";

const REPORTS: {type: ReportType; label: string}[] = [
    {type: "executive", label: "Ejecutivo"},
    {type: "technical", label: "Técnico"},
];

export const HotBar = () => {
    const [loading, setLoading] = useState<ReportType | null>(null);
    const [error, setError] = useState<string | null>(null);

    const download = async (type: ReportType) => {
        setLoading(type);
        setError(null);
        try {
            const blob = await api.generateReport(type);
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `${type}_report.pdf`;
            link.click();
            URL.revokeObjectURL(url);
        } catch (e) {
            setError(e instanceof Error ? e.message : "No se pudo generar el reporte");
        } finally {
            setLoading(null);
        }
    };

    return (
        <section className={classes["hotbar"]}>
            {REPORTS.map(({type, label}) => (
                <button key={type} className={classes[type]} disabled={loading !== null} onClick={() => download(type)}>
                    {loading === type ? "Generando..." : label}
                    <DownloadIcon />
                </button>
            ))}
            {error && <p role="alert">{error}</p>}
        </section>
    );
};
