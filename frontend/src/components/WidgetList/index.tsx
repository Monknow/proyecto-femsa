import type {FC} from "react";
import {NavLink} from "react-router";

import {cn} from "@/utils/cn";
import {Skeleton} from "@components/Skeleton";
import {WidgetWrapper} from "@components/WidgetWrapper";

import OpenIcon from "@assets/svg/open.svg?react";

import type {WidgetListProps} from "./type";
import classes from "./styles.module.css";

const SKELETON_ROWS = 5;

export const WidgetList: FC<WidgetListProps> = ({list = [], title, label, loading, className}) => {
    return (
        <WidgetWrapper title={title} className={cn(classes["widget-list"], className)}>
            <ul>
                {loading &&
                    Array.from({length: SKELETON_ROWS}, (_, i) => (
                        <li key={i}>
                            <Skeleton width="60%" height="var(--font-size-sm)" />
                            <Skeleton width="30%" height="var(--font-size-4xl)" />
                        </li>
                    ))}
                {list.map(({name, value, link}) => {
                    return (
                        <li key={name}>
                            <div className={classes["content"]}>
                                <p className={classes["name"]}>{name}</p>
                                <strong>
                                    <span className={classes["value"]}>{value}</span>
                                    <span className={classes["label"]}>{label}</span>
                                </strong>
                            </div>
                            {link && (
                                <NavLink to={link} className={classes["link"]}>
                                    <OpenIcon />
                                </NavLink>
                            )}
                        </li>
                    );
                })}
            </ul>
        </WidgetWrapper>
    );
};
