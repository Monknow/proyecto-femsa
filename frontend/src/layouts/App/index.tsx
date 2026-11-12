import {Outlet} from "react-router";

import {Navegation} from "@components/Navegation";

import classes from "./styles.module.css";
import {Page} from "../Page";

export const App = () => {
    return (
        <div className={classes["app"]}>
            <Navegation />
            <Page>
                <Outlet />
            </Page>
        </div>
    );
};
