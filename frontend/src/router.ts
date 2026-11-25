import {createElement} from "react";
import {createBrowserRouter, Navigate} from "react-router";

import {App} from "@layouts/App";
import Files from "@pages/Files";
import Home from "@pages/Home";
import Explorer from "@pages/Explorer";
import ExplorerServers from "@pages/ExplorerServers";
import Servers from "@pages/Servers";
import Vulnerabilities from "@pages/Vulnerabilities";
import Server from "@pages/Server";
import Vulnerability from "@pages/Vulnerability";

export const router = createBrowserRouter([
    {
        Component: App,
        children: [
            {
                path: "/",
                Component: Home,
            },

            {
                path: "/files",
                Component: Files,
            },
            {
                path: "/explorer",
                element: createElement(Navigate, {to: "/explorer/vulnerabilities", replace: true}),
            },
            {
                path: "/explorer/vulnerabilities",
                Component: Explorer,
            },
            {
                path: "/explorer/servers",
                Component: ExplorerServers,
            },
            {
                path: "/servers",
                Component: Servers,
            },
            {
                path: "/servers/:id",
                Component: Server,
            },
            {
                path: "/vulnerabilities",
                Component: Vulnerabilities,
            },
            {
                path: "/vulnerabilities/:id",
                Component: Vulnerability,
            },
        ],
    },
]);
