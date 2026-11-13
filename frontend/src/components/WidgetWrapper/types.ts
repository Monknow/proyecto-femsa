import type {PropsWithChildren} from "react";

export interface WidgetWrapperProps extends PropsWithChildren {
    title: string;
    className?: string;
}
