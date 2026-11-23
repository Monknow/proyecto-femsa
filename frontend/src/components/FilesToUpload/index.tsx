import {useState} from "react";
import {api} from "@/api/client";
import classes from "./styles.module.css";
import type {Props} from "./types";
import {formatBytes} from "@/utils/formatBytes";

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
            <ul>
                {files.map((file, index) => {
                    return (
                        <li key={file.name}>
                            <span className={classes["name"]}>{file.name}</span>
                            <span className={classes["date"]}>{new Date(file.lastModified).toDateString()}</span>
                            <span className={classes["size"]}>{formatBytes(file.size)}</span>
                            {errors[file.name] && <span role="alert">{errors[file.name]}</span>}
                            <button
                                className={classes["delete"]}
                                disabled={uploading}
                                onClick={() => {
                                    handleDelete(index);
                                }}>
                                x
                            </button>
                        </li>
                    );
                })}
            </ul>
            <button className={classes["confirm"]} onClick={handleConfirm} disabled={uploading}>
                {uploading ? "Subiendo..." : "Confirmar"}
            </button>
        </div>
    );
};
