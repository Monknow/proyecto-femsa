export type Server = {
    _id: string;
    os_family?: string | null;
    os_lifecycle?: string | null;
    infrastructure_type?: string | null;
    asset_type?: string | null;
    functional_role?: string | null;
    environment?: string | null;
    region_group?: string | null;
    asset_criticality?: string | null;
    cpu_capacity_band?: string | null;
    memory_capacity_band?: string | null;
    architecture_band?: string | null;
    inventory_freshness_band?: string | null;
    boot_age_band?: string | null;
    exposure_category?: string | null;
    risk_band?: string | null;
    vulnerability_volume_band?: string | null;
};
