import type {ButtonHTMLAttributes, FC, ReactNode} from "react";

import {cn} from "@/utils/cn";

import classes from "./styles.module.css";

export type ButtonVariant = "gradient" | "outline" | "solid";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    /** Optional icon (an SVG component element), rendered after the label. */
    icon?: ReactNode;
};

export const Button: FC<ButtonProps> = ({variant = "solid", icon, className, children, type = "button", ...props}) => {
    return (
        <button type={type} className={cn(classes["button"], classes[variant], className)} {...props}>
            {children}
            {icon}
        </button>
    );
};
