import type {Server} from "@/types/server";
import type {Vulnerability} from "@/types/vulnerability";
import type {FileMetadata} from "@/types/file";
import {withScore} from "@/utils/score";

// In dev the Vite proxy forwards /api/* to the FastAPI backend (see vite.config.ts).
// Set VITE_API_URL to point at a deployed backend instead.
const BASE_URL: string = import.meta.env.VITE_API_URL ?? "/api";

type ApiResponse<T> = {status: number; data: T};

export class ApiError extends Error {
    status: number;

    constructor(status: number, message: string) {
        super(message);
        this.status = status;
    }
}

// Identical in-flight requests (e.g. several Home widgets asking for all vulnerabilities) share one promise.
const inFlight = new Map<string, Promise<unknown>>();

const request = <T>(method: "GET" | "POST", path: string, body?: unknown): Promise<T> => {
    const key = `${method} ${path} ${body === undefined ? "" : JSON.stringify(body)}`;
    const existing = inFlight.get(key);
    if (existing) return existing as Promise<T>;

    const promise = (async () => {
        const response = await fetch(`${BASE_URL}${path}`, {
            method,
            headers: body === undefined ? undefined : {"Content-Type": "application/json"},
            body: body === undefined ? undefined : JSON.stringify(body),
        });

        if (!response.ok) {
            const detail = await response
                .json()
                .then((json) => json?.detail)
                .catch(() => undefined);
            throw new ApiError(response.status, typeof detail === "string" ? detail : response.statusText);
        }

        const json = (await response.json()) as ApiResponse<T>;
        return json.data;
    })().finally(() => inFlight.delete(key));

    inFlight.set(key, promise);
    return promise;
};

// Multipart upload of one Excel file; the backend validates it and loads it into the DB.
const uploadFile = async (file: File): Promise<void> => {
    const form = new FormData();
    form.append("file", file);

    // No Content-Type header: the browser sets the multipart boundary itself.
    const response = await fetch(`${BASE_URL}/db/load`, {method: "POST", body: form});

    if (!response.ok) {
        const detail = await response
            .json()
            .then((json) => json?.detail)
            .catch(() => undefined);
        const message =
            typeof detail === "string" ? detail : typeof detail?.message === "string" ? detail.message : response.statusText;
        throw new ApiError(response.status, message);
    }
};

const failFromResponse = async (response: Response): Promise<never> => {
    const detail = await response
        .json()
        .then((json) => json?.detail)
        .catch(() => undefined);
    throw new ApiError(response.status, typeof detail === "string" ? detail : response.statusText);
};

// Downloads the originally uploaded file as a Blob.
const downloadRawFile = async (id: string): Promise<Blob> => {
    const response = await fetch(`${BASE_URL}/db/files/${encodeURIComponent(id)}/download`);
    if (!response.ok) return failFromResponse(response);
    return response.blob();
};

// Deletes the file's data (and its stored raw copy) from the backend.
const deleteFile = async (id: string): Promise<void> => {
    const response = await fetch(`${BASE_URL}/db/files/${encodeURIComponent(id)}`, {method: "DELETE"});
    if (!response.ok) return failFromResponse(response);
};

export type ReportType ="executive" | "technical";

// Asks the backend to build a PDF report and returns it as a Blob for download.
const generateReport = async (reportType: ReportType): Promise<Blob> => {
    const response = await fetch(`${BASE_URL}/reports/`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({report_type: reportType}),
    });

    if (!response.ok) {
        const detail = await response
            .json()
            .then((json) => json?.detail)
            .catch(() => undefined);
        throw new ApiError(response.status, typeof detail === "string" ? detail : response.statusText);
    }

    return response.blob();
};

export type Aggregation = Record<string, number>;

export const api = {
    // Every vulnerability, with a (fallback) score attached.
    getVulnerabilities: async () => {
        const vulns = await request<Vulnerability[]>("POST", "/db/vulnerabilities/filtered", {});
        return vulns.map(withScore);
    },
    getVulnerability: async (id: string) => withScore(await request<Vulnerability>("GET", `/db/vulnerabilities/${id}`)),
    getVulnerabilityHistory: (id: string) =>
        request<FileMetadata[]>("GET", `/db/files/updates-for-vulnerability/${id}`),

    getServers: () => request<Server[]>("POST", "/db/servers/filtered", {}),
    getServer: (id: string) => request<Server>("GET", `/db/servers/${id}`),
    getServerHistory: (id: string) => request<FileMetadata[]>("GET", `/db/files/updates-for-server/${id}`),
    getFiles: () => request<FileMetadata[]>("POST", "/db/files/filtered", {}),
    uploadFile,
    downloadRawFile,
    deleteFile,
    generateReport,
    aggregateVulnerabilities: (column: keyof Vulnerability) =>
        request<Aggregation>("POST", `/db/vulnerabilities/filtered/agg?column=${column}`, {}),
    aggregateServers: (column: keyof Server) =>
        request<Aggregation>("POST", `/db/servers/filtered/agg?column=${column}`, {}),
};
