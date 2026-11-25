import type {FC} from "react";
import type {StatusProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";
import {FieldList} from "@/components/FieldList";

import classes from "./styles.module.css";

export const Status: FC<StatusProps> = ({environment, lifecycle}) => {
    return (
        <WidgetWrapper title="Estatus" className={classes["status"]}>
            <FieldList
                items={[
                    ["Ambiente", environment],
                    ["Ciclo de vida del SO", lifecycle],
                ]}
            />
        </WidgetWrapper>
    );
};
