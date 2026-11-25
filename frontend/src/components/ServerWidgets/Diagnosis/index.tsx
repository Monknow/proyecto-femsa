import type {FC} from "react";
import type {DiagnosisProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";
import {BigValue} from "@/components/DetailPage";

import classes from "./styles.module.css";

export const Diagnosis: FC<DiagnosisProps> = ({exposure}) => {
    return (
        <WidgetWrapper title="Diagnóstico" className={classes["diagnosis"]}>
            <BigValue value={exposure} tone="neutral" />
        </WidgetWrapper>
    );
};
