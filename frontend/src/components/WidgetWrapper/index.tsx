import type {FC} from "react";

import {cn} from "@utils/cn";

import type {WidgetWrapperProps} from "./types";
import classes from "./styles.module.css";

export const WidgetWrapper: FC<WidgetWrapperProps> = ({title, children, className}) => {
    return (
        <section className={cn(classes["widget-wrapper"], className)}>
            <h3>{title}</h3>
            {children}
        </section>
    );
};
