import type {FC} from "react";
import type {InfrastructureProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const Infrastructure: FC<InfrastructureProps> = ({id, infrastructure, cpu, memory, architecture}) => {
    return (
        <WidgetWrapper title="Infrastructure" className={classes["infrastructure"]}>
            <strong>ID: {id}</strong>
            <strong>Infraestructura: {infrastructure}</strong>
            <strong>CPU: {cpu}</strong>
            <strong>Memoria: {memory}</strong>
            <strong>Arquitectura: {architecture}</strong>
        </WidgetWrapper>
    );
};
