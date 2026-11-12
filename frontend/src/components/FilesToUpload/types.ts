import type {Dispatch, SetStateAction} from "react";

export type Props = {
    files: File[];
    setFiles: Dispatch<SetStateAction<File[]>>;
};
