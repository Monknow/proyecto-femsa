export type FileMetadata = {
    _id: string;
    file_name: string;
    size_mb: number;
    upload_date: string;
    records: number;
    new_vulnerabilities: number;
    fixed_vulnerabilities: number;
};
