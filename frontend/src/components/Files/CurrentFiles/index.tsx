import {useState, type FC} from "react";
import type {CurrentFilesProps} from "./types";
import {useApi} from "@/hooks/useApi";
import {api} from "@/api/client";
import {Async} from "@/components/Async";
import {Badge} from "@/components/Badge";
import {DataRow, DataRowHeader} from "@/components/DataRow";
import type {FileMetadata} from "@/types/file";

import FileIcon from "@assets/svg/file.svg?react";
import DownloadIcon from "@assets/svg/download.svg?react";

import classes from "./styles.module.css";

const ACTIONS_WIDTH = "104px";

export const CurrentFiles: FC<CurrentFilesProps> = ({refreshKey = 0, onChanged}) => {
    const files = useApi(api.getFiles, [refreshKey]);
    const [busyId, setBusyId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleDownload = async (file: FileMetadata) => {
        setBusyId(file._id);
        setError(null);
        try {
            const blob = await api.downloadRawFile(file._id);
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = file.file_name;
            link.click();
            URL.revokeObjectURL(url);
        } catch (e) {
            setError(e instanceof Error ? e.message : "No se pudo descargar el archivo");
        } finally {
            setBusyId(null);
        }
    };

    const handleDelete = async (file: FileMetadata) => {
        if (!window.confirm(`¿Eliminar "${file.file_name}" y los datos que solo este archivo aportó?`)) return;
        setBusyId(file._id);
        setError(null);
        try {
            await api.deleteFile(file._id);
            onChanged?.();
        } catch (e) {
            setError(e instanceof Error ? e.message : "No se pudo eliminar el archivo");
        } finally {
            setBusyId(null);
        }
    };

    return (
        <ul className={classes["files-list"]}>
            {error && (
                <li role="alert" className={classes["error"]}>
                    {error}
                </li>
            )}
            <Async state={files}>
                {(files) => (
                    <>
                        <DataRowHeader
                            titleLabel="Archivo"
                            labels={["Tamaño", "Registros", "Corregidas", "Nuevas", "Fecha"]}
                            actionsWidth={ACTIONS_WIDTH}
                        />
                        {files.map((file) => (
                            <DataRow
                                key={file._id}
                                title={file.file_name}
                                icon={<FileIcon />}
                                actionsWidth={ACTIONS_WIDTH}
                                details={{
                                    id: file._id,
                                    file_name: file.file_name,
                                    upload_date: file.upload_date,
                                    size_mb: `${file.size_mb} MB`,
                                    records: file.records,
                                    fixed_vulnerabilities: file.fixed_vulnerabilities,
                                    new_vulnerabilities: file.new_vulnerabilities,
                                }}
                                cells={[
                                    `${file.size_mb} MB`,
                                    file.records,
                                    <Badge tone="ok">{file.fixed_vulnerabilities}</Badge>,
                                    <Badge tone="warning">{file.new_vulnerabilities}</Badge>,
                                    file.upload_date,
                                ]}
                                actions={
                                    <>
                                        <button
                                            type="button"
                                            title="Descargar"
                                            aria-label="Descargar"
                                            disabled={busyId === file._id}
                                            onClick={() => handleDownload(file)}>
                                            <DownloadIcon />
                                        </button>
                                        <button
                                            type="button"
                                            data-danger
                                            title="Eliminar"
                                            aria-label="Eliminar"
                                            disabled={busyId === file._id}
                                            onClick={() => handleDelete(file)}>
                                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                                <path d="M9 3h6l1 2h4v2H4V5h4l1-2zm-3 6h12l-1 12H7L6 9z" />
                                            </svg>
                                        </button>
                                    </>
                                }
                            />
                        ))}
                    </>
                )}
            </Async>
        </ul>
    );
};
