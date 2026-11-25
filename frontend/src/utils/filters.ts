import type {CellValue} from "@/types/data";
import type {NumericCheck, StringCheck} from "@/types/filtering";

const compare = (
    value: number | null | undefined,
    comparable: number | undefined,
    predicate: (value: number, comparable: number) => boolean,
): boolean => value != null && comparable != null && predicate(value, comparable);

const compareString = (
    value: string | null | undefined,
    comparable: string | undefined,
    predicate: (value: string, comparable: string) => boolean,
): boolean => value != null && comparable != null && predicate(value, comparable);

export const numericFilters: Record<NumericCheck, (value: number | null | undefined, comparable?: number) => boolean> =
    {
        empty: (value) => value == null,
        "not empty": (value) => value != null,
        equal: (value, comparable) => value === comparable,
        "not equal": (value, comparable) => value !== comparable,
        greater: (value, comparable) => compare(value, comparable, (a, b) => a > b),
        less: (value, comparable) => compare(value, comparable, (a, b) => a < b),
        "greater or equal": (value, comparable) => compare(value, comparable, (a, b) => a >= b),
        "less or equal": (value, comparable) => compare(value, comparable, (a, b) => a <= b),
    };

export const stringFilters: Record<StringCheck, (value: string | null | undefined, comparable?: string) => boolean> = {
    empty: (value) => value == null,
    "not empty": (value) => value != null,
    is: (value, comparable) => value === comparable,
    "is not": (value, comparable) => value !== comparable,
    contains: (value, comparable) => compareString(value, comparable, (a, b) => a.includes(b)),
    "does not contain": (value, comparable) => compareString(value, comparable, (a, b) => !a.includes(b)),
    "starts with": (value, comparable) => compareString(value, comparable, (a, b) => a.startsWith(b)),
    "ends with": (value, comparable) => compareString(value, comparable, (a, b) => a.endsWith(b)),
};

export const filterLabels: Record<NumericCheck | StringCheck, string> = {
    empty: "está vacío",
    "not empty": "no está vacío",
    equal: "igual a",
    "not equal": "diferente de",
    greater: "mayor que",
    less: "menor que",
    "greater or equal": "mayor o igual que",
    "less or equal": "menor o igual que",
    is: "es",
    "is not": "no es",
    contains: "contiene",
    "does not contain": "no contiene",
    "starts with": "empieza con",
    "ends with": "termina con",
};

const isNumericCheck = (type: NumericCheck | StringCheck): type is NumericCheck => type in numericFilters;
const isStringCheck = (type: NumericCheck | StringCheck): type is StringCheck => type in stringFilters;

export const getFilter = (value: CellValue, type: NumericCheck | StringCheck, comparable: string | number): boolean => {
    if (type === "empty") return value == null;
    if (type === "not empty") return value != null;
    if (typeof comparable === "string" && isStringCheck(type)) {
        return stringFilters[type](typeof value === "string" ? value : null, comparable);
    }
    if (typeof comparable === "number" && isNumericCheck(type)) {
        return numericFilters[type](typeof value === "number" ? value : null, comparable);
    }
    return false;
};
