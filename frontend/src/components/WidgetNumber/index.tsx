import type {FC} from "react";
import type {WidgetNumberProps} from "./type";

import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const WidgetNumber: FC<WidgetNumberProps> = ({title, number, label}) => {
    return (
        <WidgetWrapper title={title} className={classes["widget-number"]}>
            <strong>{number}</strong>
            <p>{label}</p>
        </WidgetWrapper>
    );
};
