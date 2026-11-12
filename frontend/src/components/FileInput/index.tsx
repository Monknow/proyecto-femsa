import {useState, type ChangeEvent} from "react";
import classes from "./styles.module.css";
import {FilesToUpload} from "@components/FilesToUpload";

export const FileInput = () => {
    const [files, setFiles] = useState<File[]>([]);

    const handleFile = (event: ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            let newFiles: File[] = [];

            for (const file of event.target.files) {
                newFiles = [...newFiles, file];
            }

            setFiles(newFiles);
        }
    };

    return (
        <>
            {files.length ? (
                <FilesToUpload files={files} setFiles={setFiles} />
            ) : (
                <label htmlFor="upload" className={classes["upload-file"]}>
                    <h3>Upload File</h3>

                    <input type="file" id="upload" onChange={handleFile} multiple accept=".xlsx,.xls,.csv" />
                </label>
            )}
        </>
    );
};
