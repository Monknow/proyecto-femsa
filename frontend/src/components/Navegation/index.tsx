import {NavLink} from "react-router";

import classes from "./styles.module.css";

export const Navegation = () => {
    return (
        <nav className={classes["navegation"]}>
            <NavLink to="/" end>
                Home
            </NavLink>
            <NavLink to="/files" end>
                Files
            </NavLink>
            <NavLink to="/timeline">Timeline</NavLink>
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/explorer">Explorer</NavLink>
            <NavLink to="/vulnerabilities">Vulnerabilities</NavLink>
            <NavLink to="/servers">Servers</NavLink>
        </nav>
    );
};
