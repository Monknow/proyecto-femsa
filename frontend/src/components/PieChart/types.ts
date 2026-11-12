export interface Props<N extends string = "name", D extends string = "value"> {
    data: Array<Record<N, string> & Record<D, number> & {fill?: string}>;
    nameKey: N;
    dataKey: D;
}
