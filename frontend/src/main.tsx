import ReactDOM from "react-dom/client";
import {createBrowserRouter} from "react-router";
import {RouterProvider} from "react-router/dom";

import {App} from "@layouts/App";
import {Upload} from "@pages/Upload";
import {Dashboard} from "@pages/Dashboard";
import {Timeline} from "@pages/Timeline";
import {Home} from "@pages/Home";

import "./index.css";

const router = createBrowserRouter([
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
                path: "/upload",
                Component: Upload,
            },
            {
                path: "/timeline",
                Component: Timeline,
            },
        ],
    },
]);

const root = document.getElementById("root") as HTMLElement;

ReactDOM.createRoot(root).render(<RouterProvider router={router} />);
