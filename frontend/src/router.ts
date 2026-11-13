import {createBrowserRouter} from "react-router";

import {App} from "@layouts/App";
import {Files} from "@/pages/Files";
import {Dashboard} from "@pages/Dashboard";
import {Timeline} from "@pages/Timeline";
import {Home} from "@pages/Home";
import {Explorer} from "./pages/Explorer";
import {Servers} from "./pages/Servers";
import {Vulnerabilities} from "./pages/Vulnerabilities";

export const router = createBrowserRouter([
    {
        Component: App,
        children: [
            {
                path: "/",
                Component: Home,
            },
            {
                path: "/dashboard",
                Component: Dashboard,
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
                path: "/servers",
                Component: Servers,
            },
            {
                path: "/timeline",
                Component: Timeline,
            },
            {
                path: "/vulnerabilities",
                Component: Vulnerabilities,
            },
        ],
    },
]);
