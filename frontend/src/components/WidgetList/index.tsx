import type {FC} from "react";
import {WidgetWrapper} from "@components/WidgetWrapper";

import type {WidgetListProps} from "./type";
import classes from "./styles.module.css";

export const WidgetList: FC<WidgetListProps> = ({list, title, label}) => {
    return (
        <WidgetWrapper title={title} className={classes["widget-list"]}>
            <ul>
                {list.map(({name, value}) => {
                    return (
                        <li>
                            <p className={classes["name"]}>{name}</p>
                            <strong>
                                <span className={classes["value"]}>{value}</span>
                                <span className={classes["label"]}>{label}</span>
                            </strong>
                        </li>
                    );
                })}
            </ul>
        </WidgetWrapper>
    );
};
