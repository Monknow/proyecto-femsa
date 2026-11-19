import {useEffect, useRef, useState, type FC} from "react";

import classes from "./styles.module.css";
import type {SingleFilterProps} from "./types";
import {numericFilters, stringFilters} from "@/utils/filters";

export const SingleFilter: FC<SingleFilterProps> = ({data, columnName}) => {
    const wrapperRef = useRef<HTMLUListElement>(null);

    // Infer the column type from the first ten rows, ignoring null values.
    // If the sampled values disagree (or are all null), the type is "unknown".
    const sampledTypes = new Set(
        data
            .slice(0, 10)
            .map((row) => row[columnName])
            .filter((value) => value !== null && value !== undefined)
            .map((value) => typeof value),
    );
    const data_type: "string" | "number" | "boolean" | "unknown" =
        sampledTypes.size === 1 ? (sampledTypes.values().next().value as "string" | "number" | "boolean") : "unknown";

    const [isOpen, setIsOpen] = useState(false);

    const toggleOpen = () => {
        setIsOpen(!isOpen);
    };

    useEffect(() => {
        const handleClickListener = (event: MouseEvent) => {
            const clickedInside = wrapperRef.current?.contains(event.target as Node);

            if (clickedInside) return;
            setIsOpen(false);
        };

        document.addEventListener("mousedown", handleClickListener);

        return () => {
            document.removeEventListener("mousedown", handleClickListener);
        };
    }, []);

    return (
        <li onClick={toggleOpen} className={classes["filter-name"]}>
            {columnName}
            {isOpen && (
                <ul ref={wrapperRef} className={classes["filter-types"]}>
                    {data_type === "string" &&
                        Object.keys(stringFilters).map((name) => {
                            return <li>{name}</li>;
                        })}

                    {data_type === "number" &&
                        Object.keys(numericFilters).map((name) => {
                            return <li>{name}</li>;
                        })}
                </ul>
            )}
        </li>
    );
};
