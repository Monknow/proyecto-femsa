import type {FC} from "react";
import type {InfrastructureProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";
import {FieldList} from "@/components/FieldList";

import classes from "./styles.module.css";

export const Infrastructure: FC<InfrastructureProps> = ({id, infrastructure, cpu, memory, architecture}) => {
    return (
        <WidgetWrapper title="Infraestructura" className={classes["infrastructure"]}>
            <FieldList
                items={[
                    ["ID", id],
                    ["Infraestructura", infrastructure],
                    ["CPU", cpu],
                    ["Memoria", memory],
                    ["Arquitectura", architecture],
                ]}
            />
        </WidgetWrapper>
    );
};
