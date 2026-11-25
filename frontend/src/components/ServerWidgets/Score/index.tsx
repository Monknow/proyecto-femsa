import type {FC} from "react";
import type {ScoreProps} from "./types";

import {WidgetWrapper} from "@components/WidgetWrapper";
import {BigValue} from "@/components/DetailPage";
import {FieldList} from "@/components/FieldList";

import classes from "./styles.module.css";

export const Score: FC<ScoreProps> = ({riskBand, vulnerabilityVolume, assetCriticality, inventoryFreshness}) => {
    return (
        <WidgetWrapper title="Puntaje" className={classes["score"]}>
            <BigValue value={riskBand} />
            <FieldList
                items={[
                    ["Volumen vulnerabilidades", vulnerabilityVolume],
                    ["Criticidad del activo", assetCriticality],
                    ["Inventario", inventoryFreshness],
                ]}
            />
        </WidgetWrapper>
    );
};
