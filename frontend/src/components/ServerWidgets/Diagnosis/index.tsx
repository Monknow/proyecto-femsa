import type {FC} from "react";
import type {DiagnosisProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const Diagnosis: FC<DiagnosisProps> = ({exposure}) => {
    return (
        <WidgetWrapper title="Diagnosis" className={classes["diagnosis"]}>
            <strong>{exposure}</strong>
        </WidgetWrapper>
    );
};
