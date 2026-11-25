import type {FC} from "react";

import {WidgetWrapper} from "@components/WidgetWrapper";
import {Async} from "@/components/Async";
import {Timeline} from "@/components/DetailPage";
import {api} from "@/api/client";
import {useApi} from "@/hooks/useApi";

type HistoryProps = {
    id: string;
};

export const History: FC<HistoryProps> = ({id}) => {
    const history = useApi(() => api.getServerHistory(id), [id]);

    return (
        <WidgetWrapper title="Historial">
            <Async state={history}>{(files) => <Timeline items={files} />}</Async>
        </WidgetWrapper>
    );
};
