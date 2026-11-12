import {NavLink} from "react-router";

import classes from "./styles.module.css";

export const Navegation = () => {
    return (
        <nav className={classes["navegation"]}>
            <NavLink to="/" end>
                Home
            </NavLink>
            <NavLink to="/upload" end>
                Upload
            </NavLink>
            <NavLink to="/timeline">Timeline</NavLink>
            <NavLink to="/dashboard">Dashboard</NavLink>
        </nav>
    );
};
