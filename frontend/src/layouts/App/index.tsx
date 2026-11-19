import {Outlet} from "react-router";

import {Page} from "@layouts/Page";
import {Navegation} from "@components/Navegation";

import classes from "./styles.module.css";

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
