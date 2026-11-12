from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Literal, Dict
from models.db_schemas import Vulnerability, Server, FileMetadata

T = TypeVar("T")

AggregationData = dict[str, int]

VulnerabiltyField  = Literal[
    "_id",
    "server_id",
    "vulnerability_type_id",
    "functional_category",
    "severity",
    "finding_status",
    "age_band",
    "last_seen_band",
    "detection_frequency_band",
    "reopen_band",
    "exploitability",
    "malware_association",
    "compliance_flag",
    "port_category",
    "protocol_category",
    "encryption_context",
    "remediation_category",
    "slastatus",
    "asset_criticality",
    "finding_risk_band"
]

ServerField = Literal[
    "_id",
    "os_family",
    "os_lifecycle",
    "infrastructure_type",
    "asset_type",
    "functional_role",
    "environment",
    "region_group",
    "asset_criticality",
    "cpu_capacity_band",
    "memory_capacity_band",
    "architecture_band",
    "inventory_freshness_band",
    "boot_age_band",
    "exposure_category",
    "risk_band",
    "vulnerability_volume_band"
]

FileMetadataField = Literal[
    "_id",
    "file_name",
    "size_mb",
    "upload_date",
    "records",
    "new_vulnerabilities",
    "fixed_vulnerabilities",
    "updated_vulnerabilities",
    "updated_servers"
]

class StatusResponse(BaseModel):
  status: int

class APIResponse(BaseModel, Generic[T]):
  status: int
  data: T

class ServerResponse(APIResponse[Server]):
  pass

class VulnerabilityResponse(APIResponse[Vulnerability]):
  pass

class FileMetadataResponse(APIResponse[FileMetadata]):
  pass
  
class VulnerabilityListResponse(APIResponse[list[Vulnerability]]):
  pass

class ServerListResponse(APIResponse[list[Server]]):
  pass

class FileMetadataListResponse(APIResponse[list[FileMetadata]]):
  pass

class IdListRequest(BaseModel):
  id_list: list[str] = Field(default_factory=list, description="List of identifiers")
  
# Aggregation by Column Schema (Server Response)
class AggregationResponse(APIResponse[AggregationData]):
  pass


# -------------------------------------------------------------------------
# Filter Schemas
# -------------------------------------------------------------------------

class VulnerabilityFilter(BaseModel):
  """Filterable fields for VulnerabilityModel. All fields are optional; only
  provided (non-None) fields are applied as WHERE conditions."""
  server_id: Optional[str] = None
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
  compliance_flag: Optional[bool] = None
  port_category: Optional[str] = None
  protocol_category: Optional[str] = None
  encryption_context: Optional[str] = None
  remediation_category: Optional[str] = None
  slastatus: Optional[str] = None
  asset_criticality: Optional[str] = None
  finding_risk_band: Optional[str] = None


class ServerFilter(BaseModel):
  """Filterable fields for ServerModel. All fields are optional; only
  provided (non-None) fields are applied as WHERE conditions."""
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


class FileMetadataFilter(BaseModel):
  """Filterable fields for FileMetadataModel. All fields are optional; only
  provided (non-None) fields are applied as WHERE conditions."""
  file_name: Optional[str] = None
  records: Optional[int] = None
  new_vulnerabilities: Optional[int] = None
  fixed_vulnerabilities: Optional[int] = None


# -------------------------------------------------------------------------
# Multi-value Filter Schemas  (IN semantics — any value in the list matches)
# -------------------------------------------------------------------------

class VulnerabilityMultiFilter(BaseModel):
  """Multi-value filter for VulnerabilityModel. Each field accepts a list of
  accepted values (OR within a field, AND across fields). Only non-None /
  non-empty lists are applied as WHERE column IN (...) conditions."""
  server_id: Optional[list[str]] = None
  vulnerability_type_id: Optional[list[str]] = None
  functional_category: Optional[list[str]] = None
  severity: Optional[list[int]] = None
  finding_status: Optional[list[str]] = None
  age_band: Optional[list[str]] = None
  last_seen_band: Optional[list[str]] = None
  detection_frequency_band: Optional[list[str]] = None
  reopen_band: Optional[list[str]] = None
  exploitability: Optional[list[str]] = None
  malware_association: Optional[list[str]] = None
  compliance_flag: Optional[list[bool]] = None
  port_category: Optional[list[str]] = None
  protocol_category: Optional[list[str]] = None
  encryption_context: Optional[list[str]] = None
  remediation_category: Optional[list[str]] = None
  slastatus: Optional[list[str]] = None
  asset_criticality: Optional[list[str]] = None
  finding_risk_band: Optional[list[str]] = None


class ServerMultiFilter(BaseModel):
  """Multi-value filter for ServerModel. Each field accepts a list of
  accepted values (OR within a field, AND across fields). Only non-None /
  non-empty lists are applied as WHERE column IN (...) conditions."""
  os_family: Optional[list[str]] = None
  os_lifecycle: Optional[list[str]] = None
  infrastructure_type: Optional[list[str]] = None
  asset_type: Optional[list[str]] = None
  functional_role: Optional[list[str]] = None
  environment: Optional[list[str]] = None
  region_group: Optional[list[str]] = None
  asset_criticality: Optional[list[str]] = None
  cpu_capacity_band: Optional[list[str]] = None
  memory_capacity_band: Optional[list[str]] = None
  architecture_band: Optional[list[str]] = None
  inventory_freshness_band: Optional[list[str]] = None
  boot_age_band: Optional[list[str]] = None
  exposure_category: Optional[list[str]] = None
  risk_band: Optional[list[str]] = None
  vulnerability_volume_band: Optional[list[str]] = None


class FileMetadataMultiFilter(BaseModel):
  """Multi-value filter for FileMetadataModel. Each field accepts a list of
  accepted values (OR within a field, AND across fields). Only non-None /
  non-empty lists are applied as WHERE column IN (...) conditions."""
  file_name: Optional[list[str]] = None
  records: Optional[list[int]] = None
  new_vulnerabilities: Optional[list[int]] = None
  fixed_vulnerabilities: Optional[list[int]] = None

# -------------------------------------------------------------------------
# Aggregation by Column Schema (After Filter, so it Expands Filter Schemas)
# -------------------------------------------------------------------------

class VulnerabilityAggregation(VulnerabilityFilter):
  """A VulnerabilityFilter (Singular) is applied, then
  the data is aggregated by one of the columns. Then this
  model contains all filter options plus an aggregate by field"""
  aggregate_by: VulnerabiltyField
  
  
class ServerAggregation(ServerFilter):
  """A ServerFilter (Singular) is applied, then
  the data is aggregated by one of the columns. Then this
  model contains all filter options plus an aggregate by field"""
  aggregate_by: ServerField
  
  
class FileMetadataAggregation(FileMetadataFilter):
  """A FileMetadataMultiFilter (Plural) is applied, then
  the data is aggregated by one of the columns. Then this
  model contains all filter options plus an aggregate by field"""
  aggregate_by: FileMetadataField
  
class VulnerabilityMultiFilterAggregation(VulnerabilityMultiFilter):
  """A VulnerabilityMultiFilter (Plural) is applied, then
  the data is aggregated by one of the columns. Then this
  model contains all filter options plus an aggregate by field"""
  aggregate_by: VulnerabiltyField
  
  
class ServerMultiFilterAggregation(ServerMultiFilter):
  """A ServerMultiFilter (Plural) is applied, then
  the data is aggregated by one of the columns. Then this
  model contains all filter options plus an aggregate by field"""
  aggregate_by: ServerField
  
  
class FileMetadataMultiFilterAggregation(FileMetadataMultiFilter):
  """A FileMetadataMultiFilter (Plural) is applied, then
  the data is aggregated by one of the columns. Then this
  model contains all filter options plus an aggregate by field"""
  aggregate_by: FileMetadataField