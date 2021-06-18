import os
from datetime import datetime

from dotenv import load_dotenv
from globaleaks.utils.log import log
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceAuthenticationFailed, SalesforceMalformedRequest

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

# Salesforce credentials associated with alac chapter
# TODO:- Replace sf_instance with country code associated with salesforce instance
sf_instance = "TI"
SF_USER = os.environ.get('{}_SF_USER'.format(sf_instance))
SF_PASS = os.environ.get('{}_SF_PASS'.format(sf_instance))
SF_SECURITY_TOKEN = os.environ.get('{}_SF_SECURITY_TOKEN'.format(sf_instance))


class SalesforceGlobaLeaks:
    def __init__(self, username=None, password=None, security_token=None):
        try:
            self.sf = Salesforce(
                username=username if username else SF_USER,
                password=password if password else SF_PASS,
                security_token=security_token if security_token else SF_SECURITY_TOKEN,
            )
        except SalesforceAuthenticationFailed as error:
            log.err(error.message)

    def create_sf_task(self, url, action=None):
        user = self.sf.query("SELECT Id FROM user WHERE Username = '{}'".format(SF_USER))
        if user.get('records'):
            user_id = user.get('records')[0].get('Id')
        if action == 'create':
            description = 'Check GL - New Record Submitted.\r\nNote: GL URL :- {}'.format(url)
        elif action == 'update':
            description = 'Check GL - Record updated.\r\nNote: GL URL :- {}'.format(url)
        sf_data = {
            'Subject': 'GlobalLeaks',
            'Description': description or None,
            'OwnerId': user_id or None,
            'ActivityDate': datetime.utcnow().strftime('%Y-%m-%d'),
        }
        self.sync_data_with_sf('Task', sf_data)

    def sync_data_with_sf(self, SF_API_ID, sf_data):
        try:
            getattr(self.sf, SF_API_ID).create(sf_data)
        except SalesforceMalformedRequest as error:
            log.err(error.message.format(url=error.url, content=error.content))
        return
