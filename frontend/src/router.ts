import {createBrowserRouter} from "react-router";

import {App} from "@layouts/App";
import Files from "@pages/Files";
import Timeline from "@pages/Timeline";
import Home from "@pages/Home";
import Explorer from "@pages/Explorer";
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
                Component: Explorer,
            },
            {
                path: "/timeline",
                Component: Timeline,
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
                path: "/timeline",
                Component: Timeline,
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
