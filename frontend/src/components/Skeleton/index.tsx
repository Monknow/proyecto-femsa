import type {CSSProperties, FC} from "react";

import {cn} from "@/utils/cn";

import classes from "./styles.module.css";

type SkeletonProps = {
    width?: CSSProperties["width"];
    height?: CSSProperties["height"];
    circle?: boolean;
    className?: string;
};

// Animated placeholder shown in place of content while it loads.
export const Skeleton: FC<SkeletonProps> = ({width = "100%", height = "1em", circle, className}) => (
    <span
        aria-hidden="true"
        className={cn(classes["skeleton"], circle && classes["circle"], className)}
        style={{width, height}}
    />
);
