import {useEffect, useRef, useState, type FC, type FormEvent} from "react";

import classes from "./styles.module.css";
import type {SingleFilterProps} from "./types";
import {filterLabels, numericFilters, stringFilters} from "@/utils/filters";
import type {NumericCheck, StringCheck} from "@/types/filtering";

const noValueChecks: string[] = ["empty", "not empty"];

export const SingleFilter: FC<SingleFilterProps> = ({data, columnName, onAdd}) => {
    const wrapperRef = useRef<HTMLLIElement>(null);

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
    const [selectedType, setSelectedType] = useState<NumericCheck | StringCheck | null>(null);
    const [value, setValue] = useState("");

    const toggleOpen = () => {
        setIsOpen(!isOpen);
        setSelectedType(null);
        setValue("");
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

    const checks: (NumericCheck | StringCheck)[] =
        data_type === "string"
            ? (Object.keys(stringFilters) as StringCheck[])
            : data_type === "number"
              ? (Object.keys(numericFilters) as NumericCheck[])
              : [];

    const selectType = (type: NumericCheck | StringCheck) => {
        if (noValueChecks.includes(type)) {
            onAdd({columnName, type, comparable: ""});
            return;
        }
        setSelectedType(type);
    };

    const submit = (event: FormEvent) => {
        event.preventDefault();
        if (selectedType === null) return;

        if (data_type === "number") {
            if (value.trim() === "" || Number.isNaN(Number(value))) return;
            onAdd({columnName, type: selectedType, comparable: Number(value)});
        } else {
            onAdd({columnName, type: selectedType, comparable: value});
        }
    };

    return (
        <li ref={wrapperRef}>
            <span onClick={toggleOpen} className={classes["filter-name"]}>
                {columnName}
            </span>
            {isOpen && (
                <ul className={classes["filter-types"]}>
                    {checks.length === 0 && <li>Tipo no soportado</li>}

                    {selectedType === null &&
                        checks.map((name) => (
                            <li key={name} onClick={() => selectType(name)} className={classes["filter-type"]}>
                                {filterLabels[name]}
                            </li>
                        ))}

                    {selectedType !== null && (
                        <li>
                            <form onSubmit={submit} className={classes["form"]}>
                                <div className={classes["form-label"]}>{filterLabels[selectedType]}</div>
                                <input
                                    autoFocus
                                    type={data_type === "number" ? "number" : "text"}
                                    step="any"
                                    value={value}
                                    onChange={(event) => setValue(event.target.value)}
                                />
                                <div className={classes["actions"]}>
                                    <button type="button" onClick={() => setSelectedType(null)}>
                                        Atrás
                                    </button>
                                    <button type="submit">Agregar</button>
                                </div>
                            </form>
                        </li>
                    )}
                </ul>
            )}
        </li>
    );
};
