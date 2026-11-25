import type {FC} from "react";
import type {DetailsProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";
import {FieldList} from "@/components/FieldList";

import classes from "./styles.module.css";

export const Details: FC<DetailsProps> = ({osFamily, assetType, role, region, bootAge}) => {
    return (
        <WidgetWrapper title="Detalles" className={classes["details"]}>
            <FieldList
                items={[
                    ["Sistema operativo", osFamily],
                    ["Tipo de activo", assetType],
                    ["Rol", role],
                    ["Región", region],
                    ["Antigüedad de arranque", bootAge],
                ]}
            />
        </WidgetWrapper>
    );
};
