import classes from "./styles.module.css";
import type {Props} from "./types";
import {formatBytes} from "@/utils/formatBytes";

export const FilesToUpload = ({files, setFiles}: Props) => {
    const handleDelete = (index: number) => {
        const newFiles = files.toSpliced(index, 1);

        setFiles(newFiles);
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
                            <button
                                className={classes["delete"]}
                                onClick={() => {
                                    handleDelete(index);
                                }}>
                                X
                            </button>
                        </li>
                    );
                })}
            </ul>
            <button>Confirmar</button>
        </div>
    );
};
