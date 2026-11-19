import {useState, type FC} from "react";
import classes from "./styles.module.css";
import type {ServerProps} from "./types";
import {Link} from "react-router";

import DangerIcon from "@assets/svg/danger.svg?react";
import OpenIcon from "@assets/svg/open.svg?react";
import ArrowDownIcon from "@assets/svg/arrow_down.svg?react";

export const Server: FC<ServerProps> = ({server}) => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleIcon = () => {
        setIsOpen(!isOpen);
    };

    return (
        <li className={classes["server"]}>
            <div className={classes["frontmatter"]}>
                <DangerIcon />
                <p>{server._id} </p>
                <p>Risk: {server.risk_band}</p>
                <p>Environment: {server.environment}</p>

                <Link to={`/servers/${server._id}`} title="Open Alone">
                    <OpenIcon />
                </Link>

                <ArrowDownIcon onClick={toggleIcon} />
            </div>
            {isOpen && (
                <ul>
                    {Object.keys(server).map((key) => {
                        return (
                            <li>
                                {key}: {server[key as keyof typeof server]}
                            </li>
                        );
                    })}
                </ul>
            )}
        </li>
    );
};
