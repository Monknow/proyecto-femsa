import {useState} from "react";
import {api} from "@/api/client";
import classes from "./styles.module.css";
import type {Props} from "./types";
import {formatBytes} from "@/utils/formatBytes";
import {Button} from "../Button";
import {Badge} from "@/components/Badge";
import {DataRow, DataRowHeader} from "@/components/DataRow";

import FileIcon from "@assets/svg/file.svg?react";

const ACTIONS_WIDTH = "32px";

export const FilesToUpload = ({files, setFiles, onUploaded}: Props) => {
    const [uploading, setUploading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const handleDelete = (index: number) => {
        const newFiles = files.toSpliced(index, 1);

        setFiles(newFiles);
    };

    // Uploads sequentially; files that fail stay in the list with their error, the rest are removed.
    const handleConfirm = async () => {
        setUploading(true);
        setErrors({});

        const failed: File[] = [];
        const newErrors: Record<string, string> = {};

        for (const file of files) {
            try {
                await api.uploadFile(file);
            } catch (error) {
                failed.push(file);
                newErrors[file.name] = error instanceof Error ? error.message : String(error);
            }
        }

        setUploading(false);
        setErrors(newErrors);
        setFiles(failed);
        if (failed.length < files.length) onUploaded?.();
    };

    return (
        <div className={classes["uploaded-files"]}>
            <h2>Archivos a subir</h2>
            <ul className={classes["list"]}>
                <DataRowHeader
                    titleLabel="Archivo"
                    labels={["Fecha", "Tamaño", "Estado"]}
                    actionsWidth={ACTIONS_WIDTH}
                />
                {files.map((file, index) => {
                    const error = errors[file.name];
                    return (
                        <DataRow
                            key={file.name}
                            title={file.name}
                            icon={<FileIcon />}
                            tone={error ? "danger" : "neutral"}
                            actionsWidth={ACTIONS_WIDTH}
                            cells={[
                                new Date(file.lastModified).toLocaleDateString(),
                                formatBytes(file.size),
                                error ? (
                                    <span role="alert" title={error}>
                                        <Badge tone="danger">{error}</Badge>
                                    </span>
                                ) : (
                                    <Badge>Pendiente</Badge>
                                ),
                            ]}
                            actions={
                                <button
                                    type="button"
                                    data-danger
                                    title="Quitar"
                                    aria-label="Quitar"
                                    disabled={uploading}
                                    onClick={() => handleDelete(index)}>
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                        <path d="M18.3 5.71 12 12l6.3 6.29-1.41 1.42L10.59 13.4 4.3 19.71 2.89 18.3 9.17 12 2.89 5.71 4.3 4.3l6.29 6.3 6.29-6.3z" />
                                    </svg>
                                </button>
                            }
                        />
                    );
                })}
            </ul>
            <Button variant="gradient" onClick={handleConfirm} disabled={uploading}>
                {uploading ? "Subiendo..." : "Confirmar"}
            </Button>
        </div>
    );
};
