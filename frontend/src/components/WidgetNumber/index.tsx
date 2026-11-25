import type {FC} from "react";
import type {WidgetNumberProps} from "./type";

import {cn} from "@/utils/cn";
import {Skeleton} from "@components/Skeleton";
import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const WidgetNumber: FC<WidgetNumberProps> = ({title, number, label, loading, className}) => {
    return (
        <WidgetWrapper title={title} className={cn(classes["widget-number"], className)}>
            {loading ? (
                <>
                    <Skeleton width="4ch" height="var(--font-size-5xl)" />
                    <Skeleton width="8ch" height="var(--font-size-xs)" />
                </>
            ) : (
                <>
                    <strong>{number}</strong>
                    <p>{label}</p>
                </>
            )}
        </WidgetWrapper>
    );
};
