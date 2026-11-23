import {type FC} from "react";
import type {CurrentFilesProps} from "./types";
import {useApi} from "@/hooks/useApi";
import {api} from "@/api/client";
import {Async} from "@/components/Async";

import classes from "./styles.module.css";

export const CurrentFiles: FC<CurrentFilesProps> = ({refreshKey = 0}) => {
    const files = useApi(api.getFiles, [refreshKey]);

    return (
        <ul className={classes["files-list"]}>
            <Async state={files}>
                {(files) => {
                    return (
                        <li>
                            {files.map((file) => {
                                return (
                                    <ul key={file._id} className={classes["single-file"]}>
                                        <li>{file.file_name}</li>
                                        <li>{file._id}</li>
                                        <li>{file.size_mb} mb</li>
                                        <li>{file.records}</li>
                                        <li>{file.fixed_vulnerabilities}</li>
                                        <li>{file.new_vulnerabilities}</li>
                                        <li>{file.upload_date}</li>
                                    </ul>
                                );
                            })}
                        </li>
                    );
                }}
            </Async>
        </ul>
    );
};
