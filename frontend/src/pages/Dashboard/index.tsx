import serverData from "@/data/servers.json";
import {aggregateData} from "@/utils/aggregateData";
import {PieChart} from "@components/PieChart";

export const Dashboard = () => {
    return (
        <div>
            <PieChart data={aggregateData(serverData, "LINUX_SERVER")} dataKey="value" nameKey="name" />
            <PieChart data={aggregateData(serverData, "REGION_CENTRAL")} dataKey="value" nameKey="name" />
            <PieChart data={aggregateData(serverData, "INTERNAL")} dataKey="value" nameKey="name" />
            <PieChart data={aggregateData(serverData, "VERY_HIGH")} dataKey="value" nameKey="name" />
            <PieChart data={aggregateData(serverData, "PRODUCTION")} dataKey="value" nameKey="name" />
        </div>
    );
};
