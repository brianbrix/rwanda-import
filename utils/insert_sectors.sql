DELETE from amp_sector_indicator;
DELETE from amp_organisation_sector;
DELETE from amp_activity_sector;
DELETE from amp_sector CASCADE;
DELETE FROM amp_classification_config;
DELETE FROM amp_sector_scheme;

INSERT INTO amp_sector_scheme (amp_sec_scheme_id, sec_scheme_code, sec_scheme_name, show_in_rm)
SELECT nextval('AMP_SECTOR_SCHEME_seq'), 'NST', 'National Strategy for Transformation 1', false
WHERE NOT EXISTS (
    SELECT 1 FROM amp_sector_scheme WHERE sec_scheme_code = 'NST'
);

INSERT INTO amp_sector_scheme (amp_sec_scheme_id, sec_scheme_code, sec_scheme_name, show_in_rm)
SELECT nextval('AMP_SECTOR_SCHEME_seq'), 'PS', 'Primary Sector', false
WHERE NOT EXISTS (
    SELECT 1 FROM amp_sector_scheme WHERE sec_scheme_code = 'PVS'
);
INSERT INTO amp_classification_config(id,name,multisector,is_primary_sector,classification_id)
SELECT nextval('AMP_CLASSIFICATION_CONFIG_seq'), 'Primary', true, true, (SELECT amp_sec_scheme_id FROM amp_sector_scheme WHERE sec_scheme_code='PS' LIMIT 1)
WHERE NOT EXISTS (
    SELECT 1 FROM amp_classification_config WHERE name = 'Primary'
);
INSERT INTO amp_classification_config(id, name, multisector, is_primary_sector, classification_id)
SELECT nextval('AMP_CLASSIFICATION_CONFIG_seq'), 'Secondary', true, false, (SELECT amp_sec_scheme_id FROM amp_sector_scheme WHERE sec_scheme_code='NST' LIMIT 1)
WHERE NOT EXISTS (
    SELECT 1 FROM amp_classification_config WHERE name = 'Secondary'
);
