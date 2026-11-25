import type {TableRow} from "@/types/data";

export type ExportFormat = "pdf" | "csv" | "excel" | "json";

const FILE_NAME = "vulnerabilidades";

const getColumns = (rows: TableRow[]) => Object.keys(rows[0] ?? {});

const cellToString = (value: TableRow[string]) => (value === null ? "" : String(value));

const escapeHtml = (text: string) =>
    text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const saveBlob = (content: string, mime: string, extension: string) => {
    const url = URL.createObjectURL(new Blob([content], {type: mime}));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${FILE_NAME}.${extension}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
};

const toCsv = (rows: TableRow[]) => {
    const escape = (text: string) => (/[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text);
    const columns = getColumns(rows);
    const lines = [columns, ...rows.map((row) => columns.map((column) => cellToString(row[column])))];

    // BOM so Excel reads UTF-8 correctly
    return "﻿" + lines.map((line) => line.map(escape).join(",")).join("\r\n");
};

const toHtmlTable = (rows: TableRow[]) => {
    const columns = getColumns(rows);
    const head = columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("");
    const body = rows
        .map((row) => `<tr>${columns.map((column) => `<td>${escapeHtml(cellToString(row[column]))}</td>`).join("")}</tr>`)
        .join("");

    return `<table border="1"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
};

const toExcel = (rows: TableRow[]) =>
    `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="UTF-8"></head><body>${toHtmlTable(rows)}</body></html>`;

const printAsPdf = (rows: TableRow[]) => {
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
        return;
    }

    printWindow.document.write(`<!doctype html><html><head><meta charset="UTF-8"><title>${FILE_NAME}</title>
<style>
@page { size: landscape; margin: 10mm; }
body { font-family: sans-serif; font-size: 8px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #999; padding: 2px 4px; text-align: left; word-break: break-word; }
th { background: #eee; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
</style></head><body>${toHtmlTable(rows)}</body></html>`);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
};

export const exportData = (rows: TableRow[], format: ExportFormat) => {
    switch (format) {
        case "csv":
            saveBlob(toCsv(rows), "text/csv;charset=utf-8", "csv");
            break;
        case "json":
            saveBlob(JSON.stringify(rows, null, 2), "application/json", "json");
            break;
        case "excel":
            saveBlob(toExcel(rows), "application/vnd.ms-excel", "xls");
            break;
        case "pdf":
            printAsPdf(rows);
            break;
    }
};
