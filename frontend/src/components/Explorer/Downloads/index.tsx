import type {FC} from "react";

import classes from "./styles.module.css";
import type {DownloadsProps} from "./types";

export const Downloads: FC<DownloadsProps> = () => {
    return (
        <section className={classes["downloads"]}>
            <p>Descargar como:</p>
            <ul>
                <li>
                    <button type="button">PDF</button>
                </li>
                <li>
                    <button type="button">CSV</button>
                </li>
                <li>
                    <button type="button">Excel</button>
                </li>
                <li>
                    <button type="button">JSON</button>
                </li>
            </ul>
        </section>
    );
};
