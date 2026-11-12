import type {PropsWithChildren} from "react";

import classes from "./styles.module.css";

export const Page = ({children}: PropsWithChildren) => {
    return <main className={classes["page"]}>{children}</main>;
};
