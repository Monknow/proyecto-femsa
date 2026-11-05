import pandas as pd
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Table
from sqlalchemy.orm import relationship, class_mapper
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from .df_schemas import ServerDataFrameSchema, VulnerabilityDataFrameSchema, FileMetadataDataFrameSchema

from core.db_connection import Base


# Since MANY file updates can be linked to
# MANY vulnerabilities and MANY servers (and theese relation-
# ships should be stored in order to recons-
# truct a complete vulnerability history) then
# we create two relation tables to handle MANY to MANY
# relations

# MANY files to MANY Vulns
file_vulnerabilities_association = Table(
    "file_vulnerabilities",
    Base.metadata,
    Column("file_id", String, ForeignKey("file_metadata._id"), primary_key=True),
    Column("vulnerability_id", String, ForeignKey("vulnerabilities._id"), primary_key=True)
)

# MANY files to MANY Servers
file_servers_association = Table(
    "file_servers",
    Base.metadata,
    Column("file_id", String, ForeignKey("file_metadata._id"), primary_key=True),
    Column("server_id", String, ForeignKey("servers._id"), primary_key=True)
)

class ServerModel(Base):
  __tablename__ = "servers"

  _id = Column(String, primary_key=True, index=True)
  os_family = Column(String, nullable=True)
  os_lifecycle = Column(String, nullable=True)
  infrastructure_type = Column(String, nullable=True)
  asset_type = Column(String, nullable=True)
  functional_role = Column(String, nullable=True)
  environment = Column(String, nullable=True)
  region_group = Column(String, nullable=True)
  asset_criticality = Column(
      String, nullable=True
  )
  cpu_capacity_band = Column(String, nullable=True)
  memory_capacity_band = Column(String, nullable=True)
  architecture_band = Column(String, nullable=True)
  inventory_freshness_band = Column(String, nullable=True)
  boot_age_band = Column(String, nullable=True)
  exposure_category = Column(String, nullable=True)
  risk_band = Column(String, nullable=True)
  vulnerability_volume_band = Column(
      String, nullable=True
  )

  vulnerabilities = relationship(
      "VulnerabilityModel", back_populates="server", cascade="all, delete-orphan"
  )
  
  files = relationship(
        "FileMetadataModel",
        secondary=file_servers_association,
        back_populates="updated_servers"
  )
  
  @classmethod
  def sanitize_convert_df(cls, server_df: ServerDataFrameSchema) -> dict:
      server_column_mapping = {
            'ServerID': '_id',
            'OSFamily': 'os_family',
            'OSLifecycle': 'os_lifecycle',
            'InfrastructureType': 'infrastructure_type',
            'AssetType': 'asset_type',
            'FunctionalRole': 'functional_role',
            'Environment': 'environment',
            'RegionGroup': 'region_group',
            'AssetCriticality': 'asset_criticality',
            'CPUCapacityBand': 'cpu_capacity_band',
            'MemoryCapacityBand': 'memory_capacity_band',
            'ArchitectureBand': 'architecture_band',
            'InventoryFreshnessBand': 'inventory_freshness_band',
            'BootAgeBand': 'boot_age_band',
            'ExposureCategory': 'exposure_category',
            'RiskBand': 'risk_band',
            'VulnerabilityVolumeBand': 'vulnerability_volume_band',
        }
      s_df = server_df.copy().rename(columns=server_column_mapping)
      s_df = s_df.drop_duplicates(subset=["_id"])
      valid_server_cols = {col.name for col in ServerModel.__table__.columns}
      server_records = [
            {k: (None if pd.isna(v) else v) for k, v in row.items() if k in valid_server_cols}
            for row in s_df.to_dict(orient="records")
      ]
      
      return server_records
  
  @classmethod
  def from_dataframe(cls, servers_df: ServerDataFrameSchema) -> list['ServerModel']:
        """
        Takes a pandas DataFrame and returns a list of ServerModel instances.
        """
        
        server_column_mapping = {
            'ServerID': '_id',
            'OSFamily': 'os_family',
            'OSLifecycle': 'os_lifecycle',
            'InfrastructureType': 'infrastructure_type',
            'AssetType': 'asset_type',
            'FunctionalRole': 'functional_role',
            'Environment': 'environment',
            'RegionGroup': 'region_group',
            'AssetCriticality': 'asset_criticality',
            'CPUCapacityBand': 'cpu_capacity_band',
            'MemoryCapacityBand': 'memory_capacity_band',
            'ArchitectureBand': 'architecture_band',
            'InventoryFreshnessBand': 'inventory_freshness_band',
            'BootAgeBand': 'boot_age_band',
            'ExposureCategory': 'exposure_category',
            'RiskBand': 'risk_band',
            'VulnerabilityVolumeBand': 'vulnerability_volume_band',
        }
        
        df = servers_df.copy().rename(columns = server_column_mapping)
        
        # Convert DataFrame rows to dictionaries and unpack into model instances
        return [cls(**row) for row in df.to_dict(orient="records")]

class VulnerabilityModel(Base):
  __tablename__ = "vulnerabilities"

  _id = Column(String, primary_key=True, index=True)

  server_id = Column(
      String, ForeignKey("servers._id", ondelete="CASCADE"), nullable=False
  )

  vulnerability_type_id = Column(String, nullable=True)
  functional_category = Column(
      String, nullable=True
  )
  severity = Column(Integer, nullable=True)
  finding_status = Column(String, nullable=True)
  age_band = Column(String, nullable=True)
  last_seen_band = Column(String, nullable=True)
  detection_frequency_band = Column(String, nullable=True)
  reopen_band = Column(String, nullable=True)
  exploitability = Column(String, nullable=True)
  malware_association = Column(String, nullable=True)
  compliance_flag = Column(Boolean, default=False)
  port_category = Column(String, nullable=True)
  protocol_category = Column(String, nullable=True)
  encryption_context = Column(
      String, nullable=True
  )
  remediation_category = Column(String, nullable=True)
  slastatus = Column(String, nullable=True)
  asset_criticality = Column(String, nullable=True)
  finding_risk_band = Column(String, nullable=True)

  server = relationship("ServerModel", back_populates="vulnerabilities")
  
  files = relationship(
        "FileMetadataModel",
        secondary=file_vulnerabilities_association,
        back_populates="updated_vulnerabilities"
  )
  
  @classmethod
  def sanitize_convert_df(cls, vulnerability_df: VulnerabilityDataFrameSchema):
        # Prepare Vulnerability Records
        vuln_column_mapping = {
            'VulnerabilityID': '_id',
            'ServerID': 'server_id',
            'VulnerabilityTypeID': 'vulnerability_type_id',
            'FunctionalCategory': 'functional_category',
            'Severity': 'severity',
            'FindingStatus': 'finding_status',
            'AgeBand': 'age_band',
            'LastSeenBand': 'last_seen_band',
            'DetectionFrequencyBand': 'detection_frequency_band',
            'ReopenBand': 'reopen_band',
            'Exploitability': 'exploitability',
            'MalwareAssociation': 'malware_association',
            'ComplianceFlag': 'compliance_flag',
            'PortCategory': 'port_category',
            'ProtocolCategory': 'protocol_category',
            'EncryptionContext': 'encryption_context',
            'RemediationCategory': 'remediation_category',
            'SLAStatus': 'slastatus',
            'AssetCriticality': 'asset_criticality',
            'FindingRiskBand': 'finding_risk_band',
        }
        v_df = vulnerability_df.copy().rename(columns=vuln_column_mapping)
        v_df = v_df.drop_duplicates(subset=["_id"])
        valid_vuln_cols = {col.name for col in VulnerabilityModel.__table__.columns}
        vuln_records = [
            {k: (None if pd.isna(v) else v) for k, v in row.items() if k in valid_vuln_cols}
            for row in v_df.to_dict(orient="records")
        ]
        
        return vuln_records
  
  @classmethod
  def from_dataframe(cls, vuln_df: VulnerabilityDataFrameSchema) -> list['VulnerabilityModel']:
        """
        Takes a pandas DataFrame and returns a list of VulnerabilityModel instances.
        """
        
        vuln_column_mapping = {
            'VulnerabilityID': '_id',
            'ServerID': 'server_id',
            'VulnerabilityTypeID': 'vulnerability_type_id',
            'FunctionalCategory': 'functional_category',
            'Severity': 'severity',
            'FindingStatus': 'finding_status',
            'AgeBand': 'age_band',
            'LastSeenBand': 'last_seen_band',
            'DetectionFrequencyBand': 'detection_frequency_band',
            'ReopenBand': 'reopen_band',
            'Exploitability': 'exploitability',
            'MalwareAssociation': 'malware_association',
            'ComplianceFlag': 'compliance_flag',
            'PortCategory': 'port_category',
            'ProtocolCategory': 'protocol_category',
            'EncryptionContext': 'encryption_context',
            'RemediationCategory': 'remediation_category',
            'SLAStatus': 'slastatus',
            'AssetCriticality': 'asset_criticality',
            'FindingRiskBand': 'finding_risk_band',
        }
        
        df = vuln_df.copy().rename(columns = vuln_column_mapping)
        
        # Convert DataFrame rows to dictionaries and unpack into model instances
        return [cls(**row) for row in df.to_dict(orient="records")]
    
    


class FileMetadataModel(Base):
  __tablename__ = "file_metadata"

  _id = Column(String, primary_key=True, index=True)
  file_name = Column(String, nullable=False)
  size_mb = Column(Float, nullable=False)
  upload_date = Column(DateTime, nullable=False, default=datetime.utcnow)
  records = Column(Integer, default=0, nullable=False)
  new_vulnerabilities = Column(Integer, default=0, nullable=False)
  fixed_vulnerabilities = Column(Integer, default=0, nullable=False)
  
  updated_vulnerabilities = relationship(
        "VulnerabilityModel",
        secondary=file_vulnerabilities_association,
        back_populates="files"
  )
  
  updated_servers = relationship(
        "ServerModel",
        secondary=file_servers_association,
        back_populates="files"
  )
  
  @classmethod
  def sanitize_convert_df(cls, file_metadata_df: FileMetadataDataFrameSchema):
        # Prepare File Metadata Records
        f_df = file_metadata_df.copy().drop_duplicates(subset=["_id"])
        valid_meta_cols = {col.name for col in FileMetadataModel.__table__.columns}
        file_meta_records = [
            {k: (None if pd.isna(v) else v) for k, v in row.items() if k in valid_meta_cols}
            for row in f_df.to_dict(orient="records")
        ]
        
        return file_meta_records, f_df
  
  @classmethod
  def from_dataframe(cls, file_metadata_df: FileMetadataDataFrameSchema) -> list['FileMetadataModel']:
        """
        Takes a pandas DataFrame and returns a list of FileMetadataModel instances.
        """
        instances = []
        
        valid_columns = {col.key for col in class_mapper(cls).columns} # no relations

        for _, row in file_metadata_df.iterrows():
            # standard scalar attributes for the file metadata
            row_dict = {col: row[col] for col in valid_columns if col in row and pd.notna(row[col])}
            file_instance = cls(**row_dict)
            
            # TODO: Check this
            # # map relationship IDs for vulnerabilities
            # vuln_ids = row.get('updated_vulnerabilities')
            # if vuln_ids is not None:
            #     file_instance.updated_vulnerabilities = [
            #         VulnerabilityModel(_id=vid) for vid in vuln_ids
            #     ]

            # # map relationship IDs for servers
            # server_ids = row.get('updated_servers')
            # if server_ids is not None:
            #     file_instance.updated_servers = [
            #         ServerModel(_id=sid) for sid in server_ids
            #     ]

            instances.append(file_instance)

        return instances