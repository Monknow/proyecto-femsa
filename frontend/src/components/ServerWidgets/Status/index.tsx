import type {FC} from "react";
import type {StatusProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const Status: FC<StatusProps> = ({environment, lifecycle}) => {
    return (
        <WidgetWrapper title="Status" className={classes["status"]}>
            <strong>{environment}</strong>
            <strong>{lifecycle}</strong>
        </WidgetWrapper>
    );
};
