import {useEffect, useRef, useState, type FC} from "react";

import type {FiltersProps} from "./types";

import classes from "./styles.module.css";
import {SingleFilter} from "../SingleFilter";

export const Filters: FC<FiltersProps> = ({data, filters}) => {
    const wrapperRef = useRef<HTMLUListElement>(null);
    const newFilterRef = useRef<HTMLLIElement>(null);

    const [isOpen, setIsOpen] = useState(false);

    const columns = Object.keys(data[0] ?? {});

    const toggleOpen = () => {
        setIsOpen(!isOpen);
    };

    useEffect(() => {
        const handleClickListener = (event: MouseEvent) => {
            const clickedInside =
                newFilterRef.current === event.target || wrapperRef.current?.contains(event.target as Node);

            if (clickedInside) return;
            setIsOpen(false);
        };

        document.addEventListener("mousedown", handleClickListener);

        return () => {
            document.removeEventListener("mousedown", handleClickListener);
        };
    }, []);

    return (
        <>
            <ul className={classes["filters"]}>
                {filters.map(({columnName, type, comparable}) => {
                    return (
                        <li>
                            <code>{columnName}</code> {type} "{comparable}"
                        </li>
                    );
                })}

                <li ref={newFilterRef} onClick={toggleOpen} className={classes["new-filter"]}>
                    Nuevo Filtro
                </li>

                {columns.length === 0 && <li>Sin columnas</li>}
            </ul>
            {isOpen && (
                <ul ref={wrapperRef} className={classes["column-list"]}>
                    {columns.map((columnName) => {
                        return <SingleFilter columnName={columnName} data={data} />;
                    })}
                </ul>
            )}
        </>
    );
};
