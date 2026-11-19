import type {FC} from "react";
import type {DetailsProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const Details: FC<DetailsProps> = ({osFamily, assetType, role, region, bootAge}) => {
    return (
        <WidgetWrapper title="Details" className={classes["details"]}>
            <ul>
                <li>Sistema Operativo: {osFamily}</li>
                <li>Tipo de Activo: {assetType}</li>
                <li>Rol: {role}</li>
                <li>Región: {region}</li>
                <li>Antigüedad de Arranque: {bootAge}</li>
            </ul>
        </WidgetWrapper>
    );
};
