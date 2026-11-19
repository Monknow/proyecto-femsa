export type BaseCheck = "empty" | "not empty";

export type NumericCheck =
    | "equal"
    | "not equal"
    | "greater"
    | "less"
    | "greater or equal"
    | "less or equal"
    | BaseCheck;

export type StringCheck = "is" | "is not" | "contains" | "does not contain" | "starts with" | "ends with" | BaseCheck;

export type Filter = {
    columnName: string;
    type: NumericCheck | StringCheck;
    comparable: number | string;
};
