import {WidgetList} from "../WidgetList";
import {Async} from "@/components/Async";
import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";

const TOP = 5;

export const BackLog = () => {
    const vulnerabilities = useApi(api.getVulnerabilities);

    return (
        <Async state={vulnerabilities}>
            {(vulns) => {
                const list = vulns
                    .toSorted((a, b) => (b.score ?? 0) - (a.score ?? 0))
                    .slice(0, TOP)
                    .map(({_id, score}) => ({name: _id, value: score ?? 0}));

                return <WidgetList title="Vulnerabilidades (Prioridad)" list={list} label="score" />;
            }}
        </Async>
    );
};
