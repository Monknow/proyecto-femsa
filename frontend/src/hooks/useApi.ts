import {useEffect, useState, type DependencyList} from "react";

type State<T> = {data: T | null; error: string | null; loading: boolean};

export const useApi = <T>(fetcher: () => Promise<T>, deps: DependencyList = []): State<T> => {
    // The result is tagged with the deps it was fetched for, so a change of deps is "loading" again
    const key = JSON.stringify(deps);
    const [result, setResult] = useState<{key: string; data: T | null; error: string | null}>();

    useEffect(() => {
        let cancelled = false;

        fetcher().then(
            (data) => {
                if (!cancelled) setResult({key, data, error: null});
            },
            (error: unknown) => {
                if (!cancelled) setResult({key, data: null, error: error instanceof Error ? error.message : String(error)});
            },
        );

        return () => {
            cancelled = true;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [key]);

    if (result?.key !== key) return {data: null, error: null, loading: true};
    return {data: result.data, error: result.error, loading: false};
};
