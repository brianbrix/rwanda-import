DELETE from amp_sector_indicator;
DELETE from amp_sector CASCADE;

INSERT INTO amp_sector_scheme (amp_sec_scheme_id, sec_scheme_code, sec_scheme_name, show_in_rm)
SELECT nextval('AMP_SECTOR_SCHEME_seq'), 'PBS', 'Public Sector', false
WHERE NOT EXISTS (
    SELECT 1 FROM amp_sector_scheme WHERE sec_scheme_code = 'PBS'
);

INSERT INTO amp_sector_scheme (amp_sec_scheme_id, sec_scheme_code, sec_scheme_name, show_in_rm)
SELECT nextval('AMP_SECTOR_SCHEME_seq'), 'PVS', 'Private Sector', false
WHERE NOT EXISTS (
    SELECT 1 FROM amp_sector_scheme WHERE sec_scheme_code = 'PVS'
);
UPDATE amp_classification_config  SET classification_id = (SELECT amp_sec_scheme_id FROM amp_sector_scheme WHERE sec_scheme_code='PBS' LIMIT 1) WHERE name = 'Primary';
UPDATE amp_classification_config  SET classification_id = (SELECT amp_sec_scheme_id FROM amp_sector_scheme WHERE sec_scheme_code='PVS' LIMIT 1) WHERE name = 'Secondary';
