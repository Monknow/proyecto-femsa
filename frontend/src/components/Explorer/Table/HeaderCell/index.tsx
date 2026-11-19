import {useEffect, useRef, useState} from "react";
import {cn} from "@/utils/cn";

import type {HeaderCellProps} from "./types";

import UnsortedIcon from "@assets/svg/unsorted.svg?react";
import SortedAscendingIcon from "@assets/svg/sorted_ascending.svg?react";
import SortedDescendingIcon from "@assets/svg/sorted_descending.svg?react";
import CheckIcon from "@assets/svg/check.svg?react";

import classes from "./styles.module.css";

export const HeaderCell = ({name, sortedBy, setSortedBy}: HeaderCellProps) => {
    const wrapperRef = useRef<HTMLTableCellElement>(null);

    const isSorted = sortedBy && sortedBy.propertyName === name;

    const [isOpen, setIsOpen] = useState(false);

    const toggleIsOpen = () => {
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
        <th className={classes["header-cell"]} ref={wrapperRef}>
            <div className={cn(classes["sort-options"], isOpen ? classes["is-open"] : classes["not-open"])}>
                <button
                    type="button"
                    className={
                        isSorted && sortedBy.order == "ascending" ? classes["is-selected"] : classes["not-selected"]
                    }
                    onClick={() => {
                        setSortedBy({propertyName: name, order: "ascending"});
                        setIsOpen(false);
                    }}>
                    Sort Ascending {isSorted && sortedBy.order == "ascending" && <CheckIcon />}
                </button>
                <button
                    type="button"
                    className={
                        isSorted && sortedBy.order == "descending" ? classes["is-selected"] : classes["not-selected"]
                    }
                    onClick={() => {
                        setSortedBy({propertyName: name, order: "descending"});
                        setIsOpen(false);
                    }}>
                    Sort Descending {isSorted && sortedBy.order == "descending" && <CheckIcon />}
                </button>
                <button
                    type="button"
                    disabled={!sortedBy || sortedBy.propertyName !== name}
                    onClick={() => {
                        setSortedBy(undefined);
                        setIsOpen(false);
                    }}>
                    Remove Sort
                </button>
            </div>
            <div className={classes["header-content"]}>
                {name}
                <div onClick={toggleIsOpen} className={classes["sort-icon"]}>
                    {isSorted ? (
                        sortedBy.order === "ascending" ? (
                            <SortedAscendingIcon />
                        ) : (
                            <SortedDescendingIcon />
                        )
                    ) : (
                        <UnsortedIcon className={classes["not-sorted"]} />
                    )}
                </div>
            </div>
        </th>
    );
};
