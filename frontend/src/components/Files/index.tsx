import {useState} from "react";
import {FileInput} from "@/components/Files/FileInput";
import {CurrentFiles} from "./CurrentFiles";

import classes from "./styles.module.css";

export const Files = () => {
    // Bumped after a successful upload so the file list refetches.
    const [refreshKey, setRefreshKey] = useState(0);

    return (
        <main className={classes["files"]}>
            <h1>Archivos</h1>
            <CurrentFiles refreshKey={refreshKey} onChanged={() => setRefreshKey((key) => key + 1)} />
            <FileInput onUploaded={() => setRefreshKey((key) => key + 1)} />
        </main>
    );
};
