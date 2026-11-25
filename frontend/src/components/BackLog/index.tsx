import {WidgetList} from "../WidgetList";
import {Async} from "@/components/Async";
import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";
import type {FC} from "react";
import type {BackLogProps} from "./type";

const TOP = 5;

export const BackLog: FC<BackLogProps> = ({className}) => {
    const vulnerabilities = useApi(api.getVulnerabilities);

    return (
        <Async
            state={vulnerabilities}
            skeleton={<WidgetList className={className} title="Vulnerabilidades" label="puntaje" loading />}>
            {(vulns) => {
                const list = vulns
                    .toSorted((a, b) => (b.score ?? 0) - (a.score ?? 0))
                    .slice(0, TOP)
                    .map(({_id, score}) => ({name: _id, value: score ?? 0, link: `/vulnerabilities/${_id}`}));

                return <WidgetList className={className} title="Vulnerabilidades" list={list} label="puntaje" />;
            }}
        </Async>
    );
};
