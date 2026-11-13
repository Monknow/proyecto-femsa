import type {FC} from "react";
import type {SingleBreakdownProps} from "./type";
import classes from "./styles.module.css";

const COLORS = [
    "var(--color-emerald)",
    "var(--color-cyan)",
    "var(--color-blue)",
    "var(--color-indigo)",
    "var(--color-purple)",
    "var(--color-pink)",
];

export const SingleBreakdown: FC<SingleBreakdownProps> = ({title, data}) => {
    const totalValues = data.reduce((accum, current) => {
        return accum + current.value;
    }, 0);

    const highestLevel = data.reduce((accum, current) => {
        if (current.level) {
            return accum >= current.level ? accum : current.level;
        }

        return accum;
    }, 0);

    return (
        <li className={classes["single-breakdown"]}>
            <strong>{title}</strong>
            <div className={classes["bar"]}>
                {data.map(({name, value, level}, index) => {
                    return (
                        <div
                            className={classes["segment"]}
                            style={{
                                width: `${(value / totalValues) * 100}%`,
                                background: level
                                    ? `oklch(from var(--color-accent) ${1.25 - level / highestLevel} c h)`
                                    : COLORS[index],
                                // 1.25 so it doesn't get to 0 which is pure black
                            }}>
                            <p className={classes["tooltip"]}>
                                <span className={classes["name"]}>{name}</span>:{" "}
                                <span className={classes["value"]}>{value}</span>
                            </p>
                        </div>
                    );
                })}
            </div>
        </li>
    );
};
