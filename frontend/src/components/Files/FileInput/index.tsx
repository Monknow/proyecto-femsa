import {useRef, useState, type ChangeEvent} from "react";
import classes from "./styles.module.css";
import {FilesToUpload} from "@components/FilesToUpload";
import {Button} from "@/components/Button";

import UploadIcon from "@assets/svg/upload.svg?react";

export const FileInput = ({onUploaded}: {onUploaded?: () => void}) => {
    const [files, setFiles] = useState<File[]>([]);
    const inputRef = useRef<HTMLInputElement>(null);

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
                <FilesToUpload files={files} setFiles={setFiles} onUploaded={onUploaded} />
            ) : (
                <div className={classes["upload-file"]}>
                    <Button variant="gradient" icon={<UploadIcon />} onClick={() => inputRef.current?.click()}>
                        Subir archivo
                    </Button>

                    <input
                        ref={inputRef}
                        type="file"
                        id="upload"
                        onChange={handleFile}
                        multiple
                        accept=".xlsx,.xls,.csv"
                    />
                </div>
            )}
        </>
    );
};
