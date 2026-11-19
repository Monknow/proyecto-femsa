import {type FC} from "react"
import classes from "./styles.module.css";
import type { CurrentFilesProps } from "./types";

export const CurrentFiles: FC<CurrentFilesProps> = () => {
  return <div className={classes["current-files"]}></div>;
}