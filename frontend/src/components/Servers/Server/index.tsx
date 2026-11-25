import type {FC} from "react";
import type {ServerProps} from "./types";

import {Badge, humanize, toneFor} from "@/components/Badge";
import {DataRow} from "@/components/DataRow";

const text = (value?: string | null) => (value ? humanize(value) : "—");

export const Server: FC<ServerProps> = ({server}) => (
    <DataRow
        title={server._id}
        tone={toneFor(server.risk_band)}
        href={`/servers/${server._id}`}
        details={server}
        cells={[
            <Badge tone={toneFor(server.risk_band)}>{text(server.risk_band)}</Badge>,
            text(server.environment),
            text(server.asset_criticality),
            text(server.vulnerability_volume_band),
        ]}
    />
);
