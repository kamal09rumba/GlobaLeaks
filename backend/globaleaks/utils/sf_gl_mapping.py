from datetime import datetime

# SF IDS
SF_CLIENT_API_ID = 'TI_CaseMan__clients__c'
SF_ISSUE_API_ID = 'TI_CaseMan__Issue__c'
SF_ID = 'Id'
SF_GL_ID = 'TI_CaseMan__Globalleaks_ID__c'


def _get_valid_date(value, gl_qid, *args, **kwargs):
    if gl_qid:
        value = value.get(gl_qid)[0].get('value') if value.get(gl_qid) else None
    else:
        value = None
    # Format is 2019-05-20 00:00:00 -> 2019-05-20T00:00:00
    if value in [None, '0000-00-00 00:00:00']:
        return str(datetime.now()).replace(' ', 'T')
    value = str(value)
    return value and value.replace(' ', 'T')


def _age_modifier(value, gl_qid, *args, **kwargs):
    try:
        value = int(value.get(gl_qid)[0].get('value'))
    except (TypeError, ValueError):
        return 'Unknown'
    if value < 14:
        return '14 and under'
    if value in range(15, 25):
        return '15 - 24'
    if value in range(25, 40):
        return '25 - 39'
    if value in range(40, 55):
        return '40 - 54'
    if value > 55:
        return '55+'


def _get_name_modifier(value, gl_qid, *args, **kwargs):
    f_name = value.get(gl_qid.get('qid_first_name'))
    first_name = f_name[0].get('value') if f_name else ''
    l_name = value.get(gl_qid.get('qid_family_name'))
    family_name = l_name[0].get('value') if l_name else ''
    return ' '.join([first_name, family_name]).strip()


def _get_anonymous_modifier(value, gl_qid, *args, **kwargs):
    mapping = get_client_mapping()
    if not value.get(gl_qid):
        return None
    option_selected = value.get(gl_qid)[0].get('value')
    option_value = mapping.get('TI_CaseMan__Wants_to_remain_anonymous__c').get('options').get(option_selected)
    return option_value


def _get_how_heard_about_alac(value, gl_qid, *args, **kwargs):
    return get_client_mapping().get('TI_CaseMan__How_heard_about_ALAC__c').get('default')


def _get_location_type(value, gl_qid, *args, **kwargs):
    return get_client_mapping().get('TI_CaseMan__Location_Type__c').get('default')


def _get_location(value, gl_qid, *args, **kwargs):
    return get_client_mapping().get('TI_CaseMan__Location__c').get('default')


def _get_method_of_contact(value, gl_qid, *args, **kwargs):
    return get_client_mapping().get('TI_CaseMan__Method_of_Contact__c').get('default')


def get_id_for_sf(value, gl_qid, *args, **kwargs):
    return kwargs.get('sf_client_id')


def _get_issue_location(value, gl_qid, *args, **kwargs):
    return get_issue_mapping().get('TI_CaseMan__Location__c').get('default')


def _get_issue_type(value, gl_qid, *args, **kwargs):
    return get_issue_mapping().get('TI_CaseMan__Issue_Type__c').get('default')


def _get_primary_problem_sector(value, gl_qid, *args, **kwargs):
    return get_issue_mapping().get('TI_CaseMan__What_is_the_primary_problem_sector__c').get('default')


def get_client_mapping(*args, **kwargs):
    mapping = {
        SF_GL_ID: {'gl_qid': 'tip_id'},
        'TI_CaseMan__Wants_to_remain_anonymous__c': {
            'gl_qid': 'question_alac_whistleblower_identity',
            'options': {
                'option_alac_whistleblower_identity_yes': 'true',
                'option_alac_whistleblower_identity_no': 'false',
            },
            'modifier': _get_anonymous_modifier,
        },
        'TI_CaseMan__Name__c': {
            'gl_qid': {
                'qid_first_name': 'question_alac_whistleblower_name',
                'qid_family_name': 'question_alac_whistleblower_surname',
            },
            'modifier': _get_name_modifier,
        },
        'TI_CaseMan__Telephone_Number__c': {
            'gl_qid': 'question_alac_whistleblower_phone',
        },
        'TI_CaseMan__Email_Address__c': {
            'gl_qid': 'question_alac_whistleblower_email',
        },
        'TI_CaseMan__Age__c': {
            'gl_qid': 'question_alac_whistleblower_age',
            'modifier': _age_modifier,
        },
        'TI_CaseMan__Gender__c': {
            'gl_qid': 'question_alac_whistleblower_gender',
            'options': {
                'option_alac_whistleblower_gender_male': 'Male',
                'option_alac_whistleblower_gender_female': 'Female',
                'option_alac_whistleblower_gender_female_trans': 'Non-binary',
                'option_alac_whistleblower_gender_male_trans': 'Non-binary',
                'option_alac_whistleblower_gender_prefer_not_to_say': 'Anonym',
                'option_alac_whistleblower_gender_other': 'N/A',
            },
        },
        'TI_CaseMan__Occupation__c': {
            'gl_qid': 'question_alac_whistleblower_occupation_',
            'options': {
                'option_alac_whistleblower_occupation_public_officer': 'Civil servant / government employee',
                'option_alac_whistleblower_occupation_employee_private_sector': 'Employee in the private sector',
                'option_alac_whistleblower_occupation_employee_religious_organization': 'Employee of a religious organization',
                'option_alac_whistleblower_occupation_employee_ngo': 'Employee of a non-governmental organization',
                'option_alac_whistleblower_occupation_farmer': 'Farmer',
                'option_alac_whistleblower_occupation_homemaker': 'Homemaker',
                'option_alac_whistleblower_occupation_self_employeed': 'Self-employed',
                'option_alac_whistleblower_occupation_student': 'Student',
                'option_alac_whistleblower_occupation_retired': 'Retired',
                'option_alac_whistleblower_occupation_unenployed': 'Unemployed',
                'option_alac_whistleblower_occupation_prefer_not_to_say': 'Prefer not to say',
                'option_alac_whistleblower_occupation_other': 'Other',
            },
        },
        'TI_CaseMan__How_heard_about_ALAC__c': {
            'default': 'Other',
            'modifier': _get_how_heard_about_alac,
        },
        'TI_CaseMan__Heard_About_ALAC_Other__c': {
            'gl_qid': 'question_alac_how_did_you_ear_about_us',
        },
        'TI_CaseMan__Location_Type__c': {
            'default': 'Unknown',
            'modifier': _get_location_type,
        },
        'TI_CaseMan__Location__c': {
            'default': 'Kathmandu',
            'modifier': _get_location,
        },
        'TI_CaseMan__Method_of_Contact__c': {
            'default': 'Unknown',
            'modifier': _get_method_of_contact,
        },
        'TI_CaseMan__Received_At__c': {
            'modifier': _get_valid_date,
        },
    }
    return mapping


def get_issue_mapping(*args, **kwargs):
    mapping = {
        SF_GL_ID: {'gl_qid': 'tip_id'},
        'TI_CaseMan__Issue_Description__c': {
            'gl_qid': 'question_alac_incident_detail',
        },
        'TI_CaseMan__Location__c': {
            'default': 'N/A',
            'modifier': _get_issue_location,
        },
        'TI_CaseMan__Issue_Type__c': {
            'default': 'Other',
            'modifier': _get_issue_type,
        },
        'TI_CaseMan__What_is_the_primary_problem_sector__c': {
            'default': 'Other',
            'modifier': _get_primary_problem_sector,
        },
        'TI_CaseMan__Received_At__c': {
            'modifier': _get_valid_date,
        },
        'TI_CaseMan__Created_At__c': {
            'gl_qid': 'question_alac_incident_when',
            'modifier': _get_valid_date,
        },
        'TI_CaseMan__Client__c': {
            'modifier': get_id_for_sf,
        },
    }
    return mapping
