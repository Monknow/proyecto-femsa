import {NavLink} from "react-router";

import logo from "@assets/images/logo.webp";

import {cn} from "@/utils/cn";

import DashbordIcon from "@assets/svg/dashboard.svg?react";
import FileIcon from "@assets/svg/file.svg?react";
import ExplorerVulnerabilitiesIcon from "@assets/svg/grid_vulnerability.svg?react";
import ExplorerServersIcon from "@assets/svg/grid_server.svg?react";
import VulnerabilitiesIcon from "@assets/svg/vulnerability.svg?react";
import ServersIcon from "@assets/svg/server.svg?react";

import classes from "./styles.module.css";

export const Navegation = () => {
    return (
        <nav className={cn(classes["navegation"], "box-shadow")}>
            <img src={logo} alt="Logo de FEMSA" />
            <p className={classes["label"]}>MENÚ</p>
            <NavLink to="/" end viewTransition>
                <DashbordIcon />
                Inicio
            </NavLink>
            <NavLink to="/files" end viewTransition>
                <FileIcon />
                Archivos
            </NavLink>
            <NavLink to="/vulnerabilities" viewTransition>
                <VulnerabilitiesIcon />
                Vulnerabilidades
            </NavLink>
            <NavLink to="/servers" viewTransition>
                <ServersIcon />
                Servidores
            </NavLink>
            <p className={classes["label"]}>EXPLORADOR</p>
            <NavLink to="/explorer/vulnerabilities" viewTransition>
                <ExplorerVulnerabilitiesIcon />
                Vulnerabilidades
            </NavLink>
            <NavLink to="/explorer/servers" viewTransition>
                <ExplorerServersIcon />
                Servidores
            </NavLink>
        </nav>
    );
};
