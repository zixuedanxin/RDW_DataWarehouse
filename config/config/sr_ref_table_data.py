from config import ref_table_data as ref_constants

ref_table_conf = {
    'column_definitions': ref_constants.COLUMNS,
    'column_mappings': [
        # Columns:
        # column_map_key, phase, source_table, source_column, target_table, target_column, transformation_rule, stored_proc_name, stored_proc_created_date, created_date

        #Json to Integration
        ('1', 'lz_json', 'identification.guid', 'int_sbac_stu_reg_meta', 'guid_registration', 'clean', None),
        ('1', 'lz_json', 'identification.academicyear', 'int_sbac_stu_reg_meta', 'academic_year', 'clean', None),
        ('1', 'lz_json', 'identification.extractdate', 'int_sbac_stu_reg_meta', 'extract_date', 'srDate', None),
        ('1', 'lz_json', 'source.testregsysid', 'int_sbac_stu_reg_meta', 'test_reg_id', 'clean', None),
        # CSV to Staging
        ('1', 'lz_csv', 'statename', 'stg_sbac_stu_reg', 'name_state', 'clean', None),
        ('1', 'lz_csv', 'stateabbreviation', 'stg_sbac_stu_reg', 'code_state', 'cleanUpper', None),
        ('1', 'lz_csv', 'responsibledistrictidentifier', 'stg_sbac_stu_reg', 'guid_district', 'clean', None),
        ('1', 'lz_csv', 'organizationname', 'stg_sbac_stu_reg', 'name_district', 'clean', None),
        ('1', 'lz_csv', 'responsibleschoolidentifier', 'stg_sbac_stu_reg', 'guid_school', 'clean', None),
        ('1', 'lz_csv', 'nameofinstitution', 'stg_sbac_stu_reg', 'name_school', 'clean', None),
        ('1', 'lz_csv', 'studentidentifier', 'stg_sbac_stu_reg', 'guid_student', 'clean', None),
        ('1', 'lz_csv', 'externalssid', 'stg_sbac_stu_reg', 'external_ssid_student', 'clean', None),
        ('1', 'lz_csv', 'firstname', 'stg_sbac_stu_reg', 'name_student_first', 'clean', None),
        ('1', 'lz_csv', 'middlename', 'stg_sbac_stu_reg', 'name_student_middle', 'clean', None),
        ('1', 'lz_csv', 'lastorsurname', 'stg_sbac_stu_reg', 'name_student_last', 'clean', None),
        ('1', 'lz_csv', 'sex', 'stg_sbac_stu_reg', 'sex_student', 'srGender', None),
        ('1', 'lz_csv', 'birthdate', 'stg_sbac_stu_reg', 'birthdate_student', 'srDate', None),
        ('1', 'lz_csv', 'gradelevelwhenassessed', 'stg_sbac_stu_reg', 'grade_enrolled', 'clean', None),
        ('1', 'lz_csv', 'hispanicorlatinoethnicity', 'stg_sbac_stu_reg', 'dmg_eth_hsp', 'srYn', None),
        ('1', 'lz_csv', 'americanindianoralaskanative', 'stg_sbac_stu_reg', 'dmg_eth_ami', 'srYn', None),
        ('1', 'lz_csv', 'asian', 'stg_sbac_stu_reg', 'dmg_eth_asn', 'srYn', None),
        ('1', 'lz_csv', 'blackorafricanamerican', 'stg_sbac_stu_reg', 'dmg_eth_blk', 'srYn', None),
        ('1', 'lz_csv', 'nativehawaiianorotherpacificislander', 'stg_sbac_stu_reg', 'dmg_eth_pcf', 'srYn', None),
        ('1', 'lz_csv', 'white', 'stg_sbac_stu_reg', 'dmg_eth_wht', 'srYn', None),
        ('1', 'lz_csv', 'ideaindicator', 'stg_sbac_stu_reg', 'dmg_prg_iep', 'srYn', None),
        ('1', 'lz_csv', 'lepstatus', 'stg_sbac_stu_reg', 'dmg_prg_lep', 'srYn', None),
        ('1', 'lz_csv', 'section504status', 'stg_sbac_stu_reg', 'dmg_prg_504', 'srYn', None),
        ('1', 'lz_csv', 'economicdisadvantagestatus', 'stg_sbac_stu_reg', 'dmg_sts_ecd', 'srYn', None),
        ('1', 'lz_csv', 'migrantstatus', 'stg_sbac_stu_reg', 'dmg_sts_mig', 'srYn', None),
        ('1', 'lz_csv', 'demographicracetwoormoreraces', 'stg_sbac_stu_reg', 'dmg_multi_race', 'srYn', None),
        ('1', 'lz_csv', 'confirmationcode', 'stg_sbac_stu_reg', 'code_confirm', 'clean', None),
        ('1', 'lz_csv', 'languagecode', 'stg_sbac_stu_reg', 'code_language', 'clean', None),
        ('1', 'lz_csv', 'englishlanguageproficienclevel', 'stg_sbac_stu_reg', 'eng_prof_lvl', 'clean', None),
        ('1', 'lz_csv', 'firstentrydateintousschool', 'stg_sbac_stu_reg', 'us_school_entry_date', 'srDate', None),
        ('1', 'lz_csv', 'limitedenglishproficiencyentrydate', 'stg_sbac_stu_reg', 'lep_entry_date', 'srDate', None),
        ('1', 'lz_csv', 'lepexitdate', 'stg_sbac_stu_reg', 'lep_exit_date', 'srDate', None),
        ('1', 'lz_csv', 'titleiiilanguageinstructionprogramtype', 'stg_sbac_stu_reg', 't3_program_type', 'clean', None),
        ('1', 'lz_csv', 'primarydisabilitytype', 'stg_sbac_stu_reg', 'prim_disability_type', 'clean', None),
        # Staging to Integration
        ('3', 'stg_sbac_stu_reg', 'guid_batch', 'int_sbac_stu_reg', 'guid_batch', None, None),
        ('3', 'stg_sbac_stu_reg', 'name_state', 'int_sbac_stu_reg', 'name_state', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'code_state', 'int_sbac_stu_reg', 'code_state', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'guid_district', 'int_sbac_stu_reg', 'guid_district', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'name_district', 'int_sbac_stu_reg', 'name_district', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'guid_school', 'int_sbac_stu_reg', 'guid_school', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'name_school', 'int_sbac_stu_reg', 'name_school', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'guid_student', 'int_sbac_stu_reg', 'guid_student', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'external_ssid_student', 'int_sbac_stu_reg', 'external_ssid_student', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'name_student_first', 'int_sbac_stu_reg', 'name_student_first', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'name_student_middle', 'int_sbac_stu_reg', 'name_student_middle', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'name_student_last', 'int_sbac_stu_reg', 'name_student_last', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'birthdate_student', 'int_sbac_stu_reg', 'birthdate_student', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'sex_student', 'int_sbac_stu_reg', 'sex_student', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'grade_enrolled', 'int_sbac_stu_reg', 'grade_enrolled', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'dmg_eth_hsp', 'int_sbac_stu_reg', 'dmg_eth_hsp', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_eth_ami', 'int_sbac_stu_reg', 'dmg_eth_ami', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_eth_asn', 'int_sbac_stu_reg', 'dmg_eth_asn', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_eth_blk', 'int_sbac_stu_reg', 'dmg_eth_blk', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_eth_pcf', 'int_sbac_stu_reg', 'dmg_eth_pcf', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_eth_wht', 'int_sbac_stu_reg', 'dmg_eth_wht', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_prg_iep', 'int_sbac_stu_reg', 'dmg_prg_iep', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_prg_lep', 'int_sbac_stu_reg', 'dmg_prg_lep', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_prg_504', 'int_sbac_stu_reg', 'dmg_prg_504', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_sts_ecd', 'int_sbac_stu_reg', 'dmg_sts_ecd', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_sts_mig', 'int_sbac_stu_reg', 'dmg_sts_mig', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'dmg_multi_race', 'int_sbac_stu_reg', 'dmg_multi_race', None, 'cast({src_column} as bool)'),
        ('3', 'stg_sbac_stu_reg', 'code_confirm', 'int_sbac_stu_reg', 'code_confirm', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'code_language', 'int_sbac_stu_reg', 'code_language', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'eng_prof_lvl', 'int_sbac_stu_reg', 'eng_prof_lvl', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'us_school_entry_date', 'int_sbac_stu_reg', 'us_school_entry_date', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'lep_entry_date', 'int_sbac_stu_reg', 'lep_entry_date', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'lep_exit_date', 'int_sbac_stu_reg', 'lep_exit_date', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 't3_program_type', 'int_sbac_stu_reg', 't3_program_type', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'prim_disability_type', 'int_sbac_stu_reg', 'prim_disability_type', None, 'substr({src_column}, 1, {length})'),
        ('3', 'stg_sbac_stu_reg', 'created_date', 'int_sbac_stu_reg', 'created_date', None, None),
        #Integration to Target
        ('4', 'int_sbac_stu_reg', 'record_sid', 'student_reg', 'student_reg_rec_id', None, None),
        ('4', 'int_sbac_stu_reg', 'guid_batch', 'student_reg', 'batch_guid', None, None),
        ('4', 'int_sbac_stu_reg', 'code_state', 'student_reg', 'state_code', None, None),
        ('4', 'int_sbac_stu_reg', 'name_state', 'student_reg', 'state_name', None, None),
        ('4', 'int_sbac_stu_reg', 'guid_district', 'student_reg', 'district_guid', None, None),
        ('4', 'int_sbac_stu_reg', 'name_district', 'student_reg', 'district_name', None, None),
        ('4', 'int_sbac_stu_reg', 'guid_school', 'student_reg', 'school_guid', None, None),
        ('4', 'int_sbac_stu_reg', 'name_school', 'student_reg', 'school_name', None, None),
        ('4', 'int_sbac_stu_reg', 'guid_student', 'student_reg', 'student_guid', None, None),
        ('4', 'int_sbac_stu_reg', 'external_ssid_student', 'student_reg', 'external_student_ssid', None, None),
        ('4', 'int_sbac_stu_reg', 'name_student_first', 'student_reg', 'first_name', None, None),
        ('4', 'int_sbac_stu_reg', 'name_student_middle', 'student_reg', 'middle_name', None, None),
        ('4', 'int_sbac_stu_reg', 'name_student_last', 'student_reg', 'last_name', None, None),
        ('4', 'int_sbac_stu_reg', 'birthdate_student', 'student_reg', 'birthdate', None, None),
        ('4', 'int_sbac_stu_reg', 'sex_student', 'student_reg', 'sex', None, None),
        ('4', 'int_sbac_stu_reg', 'grade_enrolled', 'student_reg', 'enrl_grade', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_eth_hsp', 'student_reg', 'dmg_eth_hsp', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_eth_ami', 'student_reg', 'dmg_eth_ami', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_eth_asn', 'student_reg', 'dmg_eth_asn', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_eth_blk', 'student_reg', 'dmg_eth_blk', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_eth_pcf', 'student_reg', 'dmg_eth_pcf', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_eth_wht', 'student_reg', 'dmg_eth_wht', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_multi_race', 'student_reg', 'dmg_multi_race', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_prg_iep', 'student_reg', 'dmg_prg_iep', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_prg_lep', 'student_reg', 'dmg_prg_lep', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_prg_504', 'student_reg', 'dmg_prg_504', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_sts_ecd', 'student_reg', 'dmg_sts_ecd', None, None),
        ('4', 'int_sbac_stu_reg', 'dmg_sts_mig', 'student_reg', 'dmg_sts_mig', None, None),
        ('4', 'int_sbac_stu_reg', 'code_confirm', 'student_reg', 'confirm_code', None, None),
        ('4', 'int_sbac_stu_reg', 'code_language', 'student_reg', 'language_code', None, None),
        ('4', 'int_sbac_stu_reg', 'eng_prof_lvl', 'student_reg', 'eng_prof_lvl', None, None),
        ('4', 'int_sbac_stu_reg', 'us_school_entry_date', 'student_reg', 'us_school_entry_date', None, None),
        ('4', 'int_sbac_stu_reg', 'lep_entry_date', 'student_reg', 'lep_entry_date', None, None),
        ('4', 'int_sbac_stu_reg', 'lep_exit_date', 'student_reg', 'lep_exit_date', None, None),
        ('4', 'int_sbac_stu_reg', 't3_program_type', 'student_reg', 't3_program_type', None, None),
        ('4', 'int_sbac_stu_reg', 'prim_disability_type', 'student_reg', 'prim_disability_type', None, None),
        #Integration Meta to Target
        ('4', 'int_sbac_stu_reg_meta', 'guid_registration', 'student_reg', 'student_reg_guid', None, None),
        ('4', 'int_sbac_stu_reg_meta', 'academic_year', 'student_reg', 'academic_year', None, None),
        ('4', 'int_sbac_stu_reg_meta', 'extract_date', 'student_reg', 'extract_date', None, None),
        ('4', 'int_sbac_stu_reg_meta', 'test_reg_id', 'student_reg', 'reg_system_id', None, None),
    ]
}
