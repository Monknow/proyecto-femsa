const colorFor = (i: number, total: number) => `hsl(${(i * 360) / total}, 65%, 55%)`;

export const aggregateData = (rawData: Record<string, any>[], aggregatedOn: string) => {
    const datita: Record<string, number> = {};

    rawData.forEach((currentValue) => {
        datita[currentValue[aggregatedOn]] = (datita[currentValue[aggregatedOn]] ?? 0) + 1;
    });

    const entries = Object.entries(datita);

    const aggregated = entries.map(([name, value], i) => ({
        name,
        value,
        fill: colorFor(i, entries.length),
    }));

    return aggregated;
};
