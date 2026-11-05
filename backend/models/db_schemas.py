from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class Vulnerability(BaseModel):
    id: str = Field(alias="_id")
    server_id: str
    vulnerability_type_id: Optional[str] = None
    functional_category: Optional[str] = None
    severity: Optional[int] = None
    finding_status: Optional[str] = None
    age_band: Optional[str] = None
    last_seen_band: Optional[str] = None
    detection_frequency_band: Optional[str] = None
    reopen_band: Optional[str] = None
    exploitability: Optional[str] = None
    malware_association: Optional[str] = None
    compliance_flag: Optional[bool] = False
    port_category: Optional[str] = None
    protocol_category: Optional[str] = None
    encryption_context: Optional[str] = None
    remediation_category: Optional[str] = None
    slastatus: Optional[str] = None
    asset_criticality: Optional[str] = None
    finding_risk_band: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @property
    def _id(self) -> str:
        return self.id


class Server(BaseModel):
    id: str = Field(alias="_id")
    os_family: Optional[str] = None
    os_lifecycle: Optional[str] = None
    infrastructure_type: Optional[str] = None
    asset_type: Optional[str] = None
    functional_role: Optional[str] = None
    environment: Optional[str] = None
    region_group: Optional[str] = None
    asset_criticality: Optional[str] = None
    cpu_capacity_band: Optional[str] = None
    memory_capacity_band: Optional[str] = None
    architecture_band: Optional[str] = None
    inventory_freshness_band: Optional[str] = None
    boot_age_band: Optional[str] = None
    exposure_category: Optional[str] = None
    risk_band: Optional[str] = None
    vulnerability_volume_band: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @property
    def _id(self) -> str:
        return self.id


class FileMetadata(BaseModel):
    id: str = Field(alias="_id")
    file_name: str
    size_mb: float
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    records: int = 0
    new_vulnerabilities: int = 0
    fixed_vulnerabilities: int = 0
    updated_vulnerabilities: list[Union[Vulnerability, str]] = Field(default_factory=list)
    updated_servers: list[Union[Server, str]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @property
    def _id(self) -> str:
        return self.id


class FileVulnerabilityAssociation(BaseModel):
    file_id: str
    vulnerability_id: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FileServerAssociation(BaseModel):
    file_id: str
    server_id: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
