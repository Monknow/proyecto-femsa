import {type FC} from "react"
import classes from "./styles.module.css";
import type { EmptyFilterProps } from "./types";

export const EmptyFilter: FC<EmptyFilterProps> = () => {
  return <div className={classes["empty-filter"]}></div>;
}