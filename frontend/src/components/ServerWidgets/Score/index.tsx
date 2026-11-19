import type {FC} from "react";
import type {ScoreProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";

import classes from "./styles.module.css";

export const Score: FC<ScoreProps> = ({riskBand, vulnerabilityVolume, assetCriticality, inventoryFreshness}) => {
    return (
        <WidgetWrapper title="Score" className={classes["score"]}>
            <strong>{riskBand}</strong>
            <ul>
                <li>Volumen Vulnerabilidades: {vulnerabilityVolume}</li>
                <li>Criticality Asset: {assetCriticality}</li>
                <li>Inventario: {inventoryFreshness}</li>
            </ul>
        </WidgetWrapper>
    );
};
