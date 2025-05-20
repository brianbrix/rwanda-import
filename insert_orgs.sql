-- These should be run one time to clean organizations
DELETE FROM amp_user_ext;
DELETE FROM cr_documents_to_organisations;
DELETE FROM amp_org_contact;
DELETE FROM amp_organisation_sector;
DELETE FROM amp_organisation;
DELETE FROM amp_org_group;
DELETE FROM amp_org_type;

--Insert  org types
    INSERT INTO amp_org_type(amp_org_type_id,org_type,org_type_code,org_type_is_governmental,org_type_classification) VALUES
                                                                                                                              (nextval('AMP_ORG_TYPE_seq'),'Multirateral','MUL',false,'INTERNATIONAL'),
                                                                                                                              (nextval('AMP_ORG_TYPE_seq'),'Bilateral','BIL',false,'INTERNATIONAL'),
                                                                                                                              (nextval('AMP_ORG_TYPE_seq'),'Government of Rwanda(GoR)', 'PAD',true,'GOVERNMENTAL'),
                                                                                                                              (nextval('AMP_ORG_TYPE_seq'), 'Private Sector', 'PVT', false, null),
                                                                                                                              (nextval('AMP_ORG_TYPE_seq'), 'Other Organizations', 'OTH', true, null);



-- Insert org groups
INSERT INTO amp_org_group (amp_org_grp_id, org_grp_name, org_grp_code, org_type) VALUES
                                                                                     (nextval('AMP_ORG_GROUP_seq'), 'Government of Rwanda (GoR) & Ministries', 'GOR', (SELECT amp_org_type_id FROM amp_org_type WHERE org_type = 'Government of Rwanda' LIMIT 1)),
                                                                                     (nextval('AMP_ORG_GROUP_seq'), 'International Organizations & Donors', 'INT', (SELECT amp_org_type_id FROM amp_org_type WHERE org_type = 'Multilateral' LIMIT 1)),
                                                                                     (nextval('AMP_ORG_GROUP_seq'), 'NGOs & Civil Society', 'NGOS', (SELECT amp_org_type_id FROM amp_org_type WHERE org_type = 'Multilateral' LIMIT 1)),
                                                                                     (nextval('AMP_ORG_GROUP_seq'), 'Private Sector & Companies', 'PVT', (SELECT amp_org_type_id FROM amp_org_type WHERE org_type = 'Private Sector' LIMIT 1)),
                                                                                     (nextval('AMP_ORG_GROUP_seq'), 'Districts & Local Governments', 'DCTS', (SELECT amp_org_type_id FROM amp_org_type WHERE org_type = 'Government of Rwanda' LIMIT 1)),
                                                                                     (nextval('AMP_ORG_GROUP_seq'), 'Other Organizations', 'OTHER', (SELECT amp_org_type_id FROM amp_org_type WHERE org_type = 'Other Organizations' LIMIT 1))
ON CONFLICT (org_grp_name) DO NOTHING;

-- Insert GoR orgs
INSERT INTO amp_organisation (amp_org_id, name, org_code, org_grp_id)
SELECT nextval('AMP_ORGANISATION_seq'), org_name, org_code, org_grp_id
FROM (VALUES
          ('Government of Rwanda', 'GoR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Finance and Economic Planning (MINECOFIN)', 'MINECOFIN', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Agriculture and Animal Resources (MINAGRI)', 'MINAGRI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Environment (MoE)', 'MoE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Infrastructure (MININFRA)', 'MININFRA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Trade and Industry (MINICOM)', 'MINICOM', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Health (MINISANTE)', 'MINISANTE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Education (MINEDUC)', 'MINEDUC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Defense (MoD)', 'MoD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Ministry of Emergencies Management (MINEMA)', 'MINEMA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Development Board (RDB)', 'RDB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Agriculture Board (RAB)', 'RAB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('National Agricultural Export Development Board (NAEB)', 'NAEB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Environment Management Authority (REMA)', 'REMA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Forest Authority (RFA)', 'RFA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Water Resources Board (RWB)', 'RWB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Housing Authority (RHA)', 'RHA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Mines, Petroleum and Gas Board (RMB)', 'RMB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Standards Board (RSB)', 'RSB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Governance Board  (RGB)', 'RGB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Institute for Conservation Agriculture (RICA)', 'RICA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Biomedical Center (RBC)', 'RBC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Utilities Regulatory Agency (RURA)', 'RURA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Space Agency', 'RSA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Green Fund (FONERWA)', 'FONERWA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Transport Development Agency (RTDA)', 'RTDA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Development Organization (RDO)', 'RDO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Wildlife Conservation Association (RWCA)', 'RWCA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Information Society Authority (RISA)', 'RISA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Atomic Energy Board (RAEB)', 'RAEB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Technical Vocational Education & Training Board (RTB)', 'RTB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('National Land Use Authority (NLA)', 'NLA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('ARECO Rwanda Nziza', 'ARECo', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('National Industrial Research and Development Agency (NIRDA)', 'NIRDA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Local Administrative Development Agency (LODA)', 'LODA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Meteorological Agency (Meteo Rwanda)', 'METEO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda National Police (RNP)', 'RNP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Correctional Service (RCS)', 'RCS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Revenue Authoriry (RRA)', 'RRA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Environmental   Conservation Organization (RECOR)', 'RECOR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Vie et Environment Rwanda (VER)', 'VER', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Rwanda Revenue Authority (RRA)', 'RRA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('National Public Prosecution Authority (NPPA)', 'NPPA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('National Institute of Statistics of Rwanda (NISR)', 'NISR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('RWANDA TECHNICAL VOCATIONAL EDUCATION& TRAINING BOARD (RTB)', 'RTB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Lake Victoria Basin Integrated Water Resources Management Programme (LV)', 'LVP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries')),
          ('Water and Sanitation Corporation (WASAC)', 'WASAC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Government of Rwanda (GoR) & Ministries'))
     ) AS data(org_name, org_code, org_grp_id)
WHERE NOT EXISTS (SELECT 1 FROM amp_organisation WHERE name = data.org_name);

-- Insert International Organizations & Donors
INSERT INTO amp_organisation (amp_org_id, name, org_code, org_grp_id)
SELECT nextval('AMP_ORGANISATION_seq'), org_name, org_code, org_grp_id
FROM (VALUES
          ('United Nations Development Programme (UNDP)', 'UNDP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('European Cooperative for Rural Development (EUCORD)', 'EUCORD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('French Embassy (FE)', 'FE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('United Nations Children''s Fund (UNICEF)', 'UNICEF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Food and Agriculture Organization of the United Nations (FAO)', 'FAO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('World Health Organization (WHO)', 'WHO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Least Developed Countries Fund (LCDF)', 'LCDF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('World Bank (WB)', 'WB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Gates Foundation(BMGF)', 'BMGF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('African Development Fund (ADF)', 'ADF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Stichting Nederlandse Vrijwilligers (SNV)', 'SNV', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('United Nations (UN)', 'UN', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('International Monetary Fund (IMF)', 'IMF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('African Development Bank (AfDB)', 'AfDB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('European Union (EU)', 'EU', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Germany Government(GG)', 'GG', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('European Investment Bank (EIB)', 'EIB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Green Climate Fund (GCF)', 'GCF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Grid Arental', 'GA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('TradeMark East Africa (TMEA)', 'TMEA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Global Environment Facility (GEF)', 'GEF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Mitigation Action Facility (MAF)', 'MAF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Department for International Development (DFID)', 'DFID', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('International Union for Conservation of Nature (IUCN)', 'IUCN', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('International Fund for Agricultural Development (IFAD)', 'IFAD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Global Green Growth Institute (GGGI)', 'GGGI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('United Nations Office for Project Services (UNOPS)', 'UNOPS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Millennium Challenge Corporation (MCC)', 'MCC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('European Investment Fund (EIF)', 'EIF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Federal Ministry for Economic Affairs and Energy of Germany(BMWK)', 'BMWK', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Conservation International (CI)', 'CI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Asian Infrastructure Investment Bank (AIIB)', 'AIIB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('World Wildlife Fund (WWF)', 'WWF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('SNV Netherlands Development Organisation', 'SNV', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Deutsche Gesellschaft für Internationale Zusammenarbeit (GIZ)', 'GIZ', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Japan International Cooperation Agency (JICA)', 'JICA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Korea International Cooperation Agency (KOICA)', 'KOICA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Belgian agency for international cooperation (ENABEL)', 'ENABEL', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Swedish International Development Cooperation Agency (SIDA)', 'SIDA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Swiss Development Cooperation (SDC)', 'SDC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('United States Agency for International Development (USAID)', 'USAID', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('UK Foreign, Commonwealth & Development Office (FCDO)', 'FCDO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Arab Development Bank (ArDB)', 'ArDB', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('French Development Agency (AFD)', 'AFD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Cultivating New Frontiers in Agriculture (CNFA)', 'CNFA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Danish International Development Agency (DANIDA)', 'DANIDA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Netherlands Ministry of Foreign Affairs', 'NETH', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Energy Access and Quality Improvement Project(EAQIP)', 'EAQIP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('China EXIM Bank', 'CEXIM', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('India EXIM Bank', 'IEXIM', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Canadian Government', 'CG', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('CHINA', 'CHN', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('SAUDI', 'SDI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('JAPAN', 'JPN', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('KOREA', 'KR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Switzerland', 'SW', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('BELGIUM', 'BLG', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('OPEC Fund', 'OPEC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Austria', 'AUS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Italy', 'IT', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Saudi Fund for Development', 'SFD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('German Federal Ministry for the Environment, Nature Conservation, Nuclear Safety and Consumer Protection', 'BMUV', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Adaptation Fund', 'AF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Netherlands', 'ND', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('KFW Development  Bank', 'KfW', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('United Nations Industrial Development Organization(UNIDO)', 'UNIDO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Bezos Earth Fund', 'BEZOS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('International Development Association', 'IDA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Nordic Climate Facility (NCF)', 'NCF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('German Federal Ministry for Economic Cooperation and Dvpt (BMZ)', 'BMZ', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Buffet Foundation', 'BUFFET', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('International Council for Local Environmental Initiatives(ICLEI)', 'ICLEI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('EXIM BANK OF INDIA', 'EBI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Nationally Appropriate Mitigation Actions(NAMA)', 'NAMA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('BELGIAN TECHNICAL COOPERATION', 'BTC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('CAEP', 'CAEP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('NDC Partneship  Support Unit', 'NPCU', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Danish Outdoor Council', 'DOC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('US State Department', 'USD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Swedish Environmental Protection Agency', 'SEPA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Ozone Secretariat', 'OS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Civil Society in Development', 'CISU', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('United Nations Framework Convention on Climate Change (UNFCCC)', 'UNFCCC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Embassy of the Kingdom of the Netherlands in Rwanda', 'ENK', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Water for People', 'WfP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Global Fund', 'GF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('West Chester University', 'WCU', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('National geographic society', 'NATGEO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('UN-HABITAT', 'UN-HABITAT', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Italian Ministry of Environment,  Lands and Seas(IMELS)', 'IMELS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Living water international', 'LWI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors')),
          ('Howard G. Buffet Foundation', 'HGBF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'International Organizations & Donors'))
     ) AS data(org_name, org_code, org_grp_id)
WHERE NOT EXISTS (SELECT 1 FROM amp_organisation WHERE name = data.org_name);
-- Insert NGOs & Civil Society
INSERT INTO amp_organisation (amp_org_id, name, org_code, org_grp_id)
SELECT nextval('AMP_ORGANISATION_seq'), org_name, org_code, org_grp_id
FROM (VALUES
          ('DUHAMIC-ADRI', 'DUHAMIC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Albertine Rift Conservation Society (ARCOS)', 'ARCOS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Africa50', 'Africa50', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Foundation Audemars-Watkins', 'FAW', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Livelihoods Fund SICAV SIF', 'LCF2', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Rainforest Track', 'RT', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Water aid Rwanda', 'WAR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Forest of Hope Association (FHA)', 'FHA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Worldlife conservation society', 'WCS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Rwanda Environmental Conservation Organization (RECOR)', 'RECOR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Dian Fossey Gorilla Fund International (DFGFI)', 'DFGFI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Rural Environment and Development Organization (REDO)', 'REDO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Action pour la Protection de l''Environnement et la Promotion des Filieres Agricoles (APEFA)', 'APEFA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Vie et Environnement Rwanda (VER)', 'VER', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Collectif des Artisans de la Paix et la Reconciliation (CAPR)', 'CAPR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Rwanda Environmental NGOs Forum (RENGOF)', 'RENGOF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('International Tree Foundation (ITF)', 'ITF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('One Tree Planted (OTP)', 'OTP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Livelihoods Fund', 'LIVELIHOODS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Energising Development', 'ED', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Wilderness Safaris', 'WILDERNESS', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Likano Development GmbH', 'LIKANO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Skat Consulting Rwanda', 'SKAT', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('ECOFIX Ltd', 'ECOFIX', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('AMPERSTAND Rwanda Ltd', 'AMPERSTAND', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Ntare School Old Boys Association (NSOBA)', 'NSOBA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('Save Generations Organization (SGO)', 'SGO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('LDCFII', 'LDCFII', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('United Nations High Commissioner for Refugees(UNHCR)', 'UNHCR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('World Agroforestry Centre(ICRAF)', 'ICRAF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('INADES-Formation Rwanda', 'IND', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society')),
          ('The Future in Our Minds Rwanda (FIOM Rwanda)', 'FIOM', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'NGOs & Civil Society'))
     ) AS data(org_name, org_code, org_grp_id)
WHERE NOT EXISTS (SELECT 1 FROM amp_organisation WHERE name = data.org_name);
-- Insert Private Sector & Companies
INSERT INTO amp_organisation (amp_org_id, name, org_code, org_grp_id)
SELECT nextval('AMP_ORGANISATION_seq'), org_name, org_code, org_grp_id
FROM (VALUES
          ('Gako Meat Company Ltd', 'GAKO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Development Bank of Rwanda (BRD)', 'BRD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Business Development Fund (BDF)', 'BDF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Ntare School Old Boys Association(NSOBA)', 'NSOBA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Wilderness Safari_Rwanda', 'WSR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Cattle Ville Ranchers', 'CVR', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Gako Beef Company Ltd', 'GBC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Renewgreen Ltd', 'RENEWGREEN', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('NETAFIM', 'NETAFIM', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('OCP-AFRICA-MOROCCO', 'OCP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('RPCL (Rwanda)', 'RPCL', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('SE4All', 'SE4ALL', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('ReforestAction (RA)', 'RA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('AstraZeneca (ASTRA)', 'ASTRA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('METITO (Water Solutions)', 'METITO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Ampersand Rwanda Ltd', 'AMPER', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies')),
          ('Kigali Water Ltd', 'KWL', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Private Sector & Companies'))
     ) AS data(org_name, org_code, org_grp_id)
WHERE NOT EXISTS (SELECT 1 FROM amp_organisation WHERE name = data.org_name);
-- Insert Districts & Local Governments
INSERT INTO amp_organisation (amp_org_id, name, org_code, org_grp_id)
SELECT nextval('AMP_ORGANISATION_seq'), org_name, org_code, org_grp_id
FROM (VALUES
          ('City of Kigali (CoK)', 'COK', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Transport operators', 'To', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Rwamagana District', 'RWAMAGANA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Muhanga District', 'MUHANGA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Musanze District', 'MUSANZE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Rubavu District', 'RUBAVU', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Nyagatare District', 'NYAGATARE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Rusizi District', 'RUSIZI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Nyanza District', 'NYANZA', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Huye District', 'HUYE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Karongi District', 'KARONGI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Gicumbi District', 'GICUMBI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments')),
          ('Ngororero District', 'NGORORERO', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Districts & Local Governments'))
     ) AS data(org_name, org_code, org_grp_id)
WHERE NOT EXISTS (SELECT 1 FROM amp_organisation WHERE name = data.org_name);
-- Insert Other Organizations
INSERT INTO amp_organisation (amp_org_id, name, org_code, org_grp_id)
SELECT nextval('AMP_ORGANISATION_seq'), org_name, org_code, org_grp_id
FROM (VALUES
          ('Not identified', 'NI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('diverse', 'DE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Development partners', 'DP', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('To be determined', 'TBD', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Domestic Financing', 'DOMESTIC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Basket Fund and Grants', 'BASKET', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Private Sector Federation (PSF)', 'PSF', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Rwanda Rural Rehabilitation Initiatives (RWARRI)', 'RWARRI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Rwanda Energy Group (REG)', 'REG', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Energy Development Corporation Ltd (EDCL)', 'EDCL', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Kigali Electricity Utility (EUCL)', 'EUCL', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('NDC Partnership Support Unit', 'NDC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Lake Victoria Basin Commission', 'LVBC', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('International Climate Initiative (IKI)', 'IKI', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('Investing for Employment (IFE)', 'IFE', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations')),
          ('West Chester University (Partner)', 'WCU', (SELECT amp_org_grp_id FROM amp_org_group WHERE org_grp_name = 'Other Organizations'))
     ) AS data(org_name, org_code, org_grp_id)
WHERE NOT EXISTS (SELECT 1 FROM amp_organisation WHERE name = data.org_name);
