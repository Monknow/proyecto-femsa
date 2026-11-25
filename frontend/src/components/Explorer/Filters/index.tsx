import {useEffect, useRef, useState, type FC} from "react";

import type {Filter} from "@/types/filtering";
import type {FiltersProps} from "./types";

import classes from "./styles.module.css";
import {filterLabels} from "@/utils/filters";
import {SingleFilter} from "../SingleFilter";

export const Filters: FC<FiltersProps> = ({data, filters, setFilters}) => {
    const wrapperRef = useRef<HTMLUListElement>(null);
    const newFilterRef = useRef<HTMLLIElement>(null);

    const [isOpen, setIsOpen] = useState(false);

    const columns = Object.keys(data[0] ?? {});

    const toggleOpen = () => {
        setIsOpen(!isOpen);
    };

    const addFilter = (filter: Filter) => {
        setFilters((current) => [...current, filter]);
        setIsOpen(false);
    };

    const removeFilter = (index: number) => {
        setFilters((current) => current.filter((_, i) => i !== index));
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
                {filters.map(({columnName, type, comparable}, index) => {
                    const hasValue = type !== "empty" && type !== "not empty";
                    return (
                        <li key={`${columnName}-${type}-${comparable}-${index}`} className={classes["filter-chip"]}>
                            <button
                                type="button"
                                className={classes["remove-filter"]}
                                aria-label="Quitar filtro"
                                onClick={() => removeFilter(index)}
                            >
                                ×
                            </button>
                            <code>{columnName}</code>
                            <span className={classes["filter-value"]}>
                                {filterLabels[type]} {hasValue && `"${comparable}"`}
                            </span>
                        </li>
                    );
                })}

                <li ref={newFilterRef} onClick={toggleOpen} className={classes["new-filter"]}>
                    + Nuevo Filtro
                </li>

                {columns.length === 0 && <li className={classes["empty-columns"]}>Sin columnas</li>}

                {filters.length > 0 && (
                    <li className={classes["clear-filters"]}>
                        <button type="button" onClick={() => setFilters([])}>
                            × Limpiar filtros
                        </button>
                    </li>
                )}
            </ul>
            {isOpen && (
                <ul ref={wrapperRef} className={classes["column-list"]}>
                    <li className={classes["column-list-title"]}>Filtrar por columna</li>
                    {columns.map((columnName) => {
                        return <SingleFilter key={columnName} columnName={columnName} data={data} onAdd={addFilter} />;
                    })}
                </ul>
            )}
        </>
    );
};
