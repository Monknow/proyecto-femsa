import type {Vulnerability} from "@/types/vulnerability";

// The API does not return a `score` yet. Until it does, derive a rough priority score from the
// fields we do have so the UI can still rank vulnerabilities. If the API starts sending `score`
// it is used as-is and this fallback is ignored.
const CRITICALITY_WEIGHT: Record<string, number> = {
    LOW: 0,
    MEDIUM: 5,
    HIGH: 10,
    VERY_HIGH: 15,
    CRITICAL: 20,
};

export const fallbackScore = (vuln: Vulnerability): number => {
    let score = (vuln.severity ?? 0) * 20;
    if (vuln.exploitability === "KNOWN_OR_AVAILABLE") score += 25;
    if (vuln.malware_association === "ASSOCIATED") score += 25;
    if (vuln.slastatus === "BREACHED") score += 10;
    score += CRITICALITY_WEIGHT[vuln.asset_criticality ?? ""] ?? 0;
    return score;
};

export const withScore = (vuln: Vulnerability): Vulnerability => ({
    ...vuln,
    score: vuln.score ?? fallbackScore(vuln),
});
