import type {PropsWithChildren} from "react";

import classes from "./styles.module.css";
import {cn} from "@/utils/cn";

export const Page = ({children}: PropsWithChildren) => {
    return <main className={cn(classes["page"], "box-shadow")}>{children}</main>;
};
