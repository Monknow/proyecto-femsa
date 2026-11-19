import type {ReactNode} from "react";

type AsyncProps<T> = {
    state: {data: T | null; error: string | null; loading: boolean};
    children: (data: T) => ReactNode;
};

// Renders loading / error placeholders until the data is available.
export const Async = <T,>({state, children}: AsyncProps<T>) => {
    if (state.error) return <p>Error: {state.error}</p>;
    if (state.loading || state.data === null) return <p>Cargando...</p>;
    return <>{children(state.data)}</>;
};
