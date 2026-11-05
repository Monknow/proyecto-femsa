import pandas as pd
import pandera.pandas as pa
from pandera.typing import DataFrame, Series

from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field

class ServerDataFrameSchema(pa.DataFrameModel):
    """
    Pandera schema validating the exact columns and types for the server DataFrame.
    """
    ServerID: Series[str] = pa.Field(alias="ServerID")
    OSFamily: Optional[Series[str]] = pa.Field(nullable=True, alias="OSFamily")
    OSLifecycle: Optional[Series[str]] = pa.Field(nullable=True, alias="OSLifecycle")
    InfrastructureType: Optional[Series[str]] = pa.Field(nullable=True, alias="InfrastructureType")
    AssetType: Optional[Series[str]] = pa.Field(nullable=True, alias="AssetType")
    FunctionalRole: Optional[Series[str]] = pa.Field(nullable=True, alias="FunctionalRole")
    Environment: Optional[Series[str]] = pa.Field(nullable=True, alias="Environment")
    RegionGroup: Optional[Series[str]] = pa.Field(nullable=True, alias="RegionGroup")
    AssetCriticality: Optional[Series[str]] = pa.Field(nullable=True, alias="AssetCriticality")
    CPUCapacityBand: Optional[Series[str]] = pa.Field(nullable=True, alias="CPUCapacityBand")
    MemoryCapacityBand: Optional[Series[str]] = pa.Field(nullable=True, alias="MemoryCapacityBand")
    ArchitectureBand: Optional[Series[str]] = pa.Field(nullable=True, alias="ArchitectureBand")
    InventoryFreshnessBand: Optional[Series[str]] = pa.Field(nullable=True, alias="InventoryFreshnessBand")
    BootAgeBand: Optional[Series[str]] = pa.Field(nullable=True, alias="BootAgeBand")
    ExposureCategory: Optional[Series[str]] = pa.Field(nullable=True, alias="ExposureCategory")
    RiskBand: Optional[Series[str]] = pa.Field(nullable=True, alias="RiskBand")
    VulnerabilityVolumeBand: Optional[Series[str]] = pa.Field(nullable=True, alias="VulnerabilityVolumeBand")

    class Config:
        # Prevents unexpected extra columns from passing silently
        strict = True  
        # Ensures types are coerced (e.g., float NaN to None/object if needed)
        coerce = True  
        
class VulnerabilityDataFrameSchema(pa.DataFrameModel):
    """
    Pandera schema validating the exact columns and types for the vulnerability DataFrame.
    """
    VulnerabilityID: Series[str] = pa.Field(alias="VulnerabilityID")
    ServerID: Series[str] = pa.Field(alias="ServerID")
    VulnerabilityTypeID: Optional[Series[str]] = pa.Field(nullable=True, alias="VulnerabilityTypeID")
    FunctionalCategory: Optional[Series[str]] = pa.Field(nullable=True, alias="FunctionalCategory")
    Severity: Optional[Series[int]] = pa.Field(nullable=True, alias="Severity")
    FindingStatus: Optional[Series[str]] = pa.Field(nullable=True, alias="FindingStatus")
    AgeBand: Optional[Series[str]] = pa.Field(nullable=True, alias="AgeBand")
    LastSeenBand: Optional[Series[str]] = pa.Field(nullable=True, alias="LastSeenBand")
    DetectionFrequencyBand: Optional[Series[str]] = pa.Field(nullable=True, alias="DetectionFrequencyBand")
    ReopenBand: Optional[Series[str]] = pa.Field(nullable=True, alias="ReopenBand")
    Exploitability: Optional[Series[str]] = pa.Field(nullable=True, alias="Exploitability")
    MalwareAssociation: Optional[Series[str]] = pa.Field(nullable=True, alias="MalwareAssociation")
    ComplianceFlag: Optional[Series[bool]] = pa.Field(nullable=True, alias="ComplianceFlag")
    PortCategory: Optional[Series[str]] = pa.Field(nullable=True, alias="PortCategory")
    ProtocolCategory: Optional[Series[str]] = pa.Field(nullable=True, alias="ProtocolCategory")
    EncryptionContext: Optional[Series[str]] = pa.Field(nullable=True, alias="EncryptionContext")
    RemediationCategory: Optional[Series[str]] = pa.Field(nullable=True, alias="RemediationCategory")
    SLAStatus: Optional[Series[str]] = pa.Field(nullable=True, alias="SLAStatus")
    AssetCriticality: Optional[Series[str]] = pa.Field(nullable=True, alias="AssetCriticality")
    FindingRiskBand: Optional[Series[str]] = pa.Field(nullable=True, alias="FindingRiskBand")

    class Config:
        strict = True  # Ensures no unexpected extra columns are included
        coerce = True  # Automatically handles type coercion where needed
        
class FileMetadataDataFrameSchema(pa.DataFrameModel):
    """
    Pandera schema validating columns and types for the file metadata DataFrame.
    """
    id: Series[str] = pa.Field(alias="_id")
    file_name: Series[str] = pa.Field(alias="file_name")
    size_mb: Series[float] = pa.Field(alias="size_mb")
    upload_date: Series[pd.Timestamp] = pa.Field(alias="upload_date")
    records: Series[int] = pa.Field(alias="records")
    new_vulnerabilities: Series[int] = pa.Field(alias="new_vulnerabilities")
    fixed_vulnerabilities: Series[int] = pa.Field(alias="fixed_vulnerabilities")
    updated_vulnerabilities: Series[object] = pa.Field(alias="updated_vulnerabilities")
    updated_servers: Series[object] = pa.Field(alias="updated_servers")

    class Config:
        strict = True  # Ensures no unexpected extra columns are included
        coerce = True  # Automatically handles type coercion where needed