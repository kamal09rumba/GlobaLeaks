import base64
import os

from dotenv import load_dotenv
from globaleaks.settings import Settings
from globaleaks.utils import sf_gl_mapping
from globaleaks.utils.crypto import GCE
from globaleaks.utils.log import log
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import (SalesforceAuthenticationFailed,
                                          SalesforceMalformedRequest)

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path)

# Salesforce credentials associated with alac chapter
# TODO:- Replace sf_instance with country code associated with salesforce instance
sf_instance = "TI"
SF_USER = os.environ.get('{}_SF_USER'.format(sf_instance))
SF_PASS = os.environ.get('{}_SF_PASS'.format(sf_instance))
SF_SECURITY_TOKEN = os.environ.get('{}_SF_SECURITY_TOKEN'.format(sf_instance))


class SalesforceGlobaLeaks:
    def __init__(self, username="", password="", security_token=""):
        self.SF_CLIENT_API_ID = sf_gl_mapping.SF_CLIENT_API_ID
        self.SF_ISSUE_API_ID = sf_gl_mapping.SF_ISSUE_API_ID
        self.SF_ID = sf_gl_mapping.SF_ID
        self.SF_GL_ID = sf_gl_mapping.SF_GL_ID
        self.client_mapping = sf_gl_mapping.get_client_mapping()
        self.issue_mapping = sf_gl_mapping.get_issue_mapping()
        try:
            self.sf = Salesforce(
                username=username if username else SF_USER,
                password=password if password else SF_PASS,
                security_token=security_token if security_token else SF_SECURITY_TOKEN,
            )
        except SalesforceAuthenticationFailed as error:
            log.error(error.message)
            raise error

    def _total_gl_records_in_sf(self):
        total_records = self.sf.query(
            'SELECT {} FROM {} WHERE {} != NULL'.format(self.SF_GL_ID, self.SF_CLIENT_API_ID, self.SF_GL_ID))
        return [gl_id.get(self.SF_GL_ID) for gl_id in total_records['records']]

    def _get_gl_data(self, decrypted_answers, gl_answers, existing_data_in_sf, mapping):
        return {
            **{
                sf_field_id: gl_question.get('modifier')(
                    decrypted_answers,
                    gl_question.get('gl_qid'),
                    sf_client_id=existing_data_in_sf.get(gl_answers.get('tip_id')),
                )
                if 'modifier' in gl_question
                else gl_question['options'].get(gl_answers.get(gl_question['gl_qid']))
                if 'options' in gl_question
                else gl_answers.get(gl_question['gl_qid'])
                for sf_field_id, gl_question in mapping.items()
            },
        }

    def _get_sf_data(self, SF_API_ID):
        return {
            r[self.SF_GL_ID]: r[self.SF_ID]
            for r in self.sf.query('Select {}, {} from {}'.format(self.SF_ID, self.SF_GL_ID, SF_API_ID))['records']
        }

    def _get_sf_attachments(self):
        FILES_BASE_PATH = Settings.working_path
        return {
            doc['PathOnClient']: (doc['Id'], doc['ContentDocumentId'])
            for doc in self.sf.bulk.ContentVersion.query('Select Id, PathOnClient, ContentDocumentId from ContentVersion')
            if doc['PathOnClient'] and doc['PathOnClient'].startswith(FILES_BASE_PATH)
        }

    def sync_attachments(self, tip_key, gl_id, existing_data_in_sf, attachments):
        EXISTING_DOCUMENTS_IN_SF = self._get_sf_attachments()
        sf_referrence_id = existing_data_in_sf.get(gl_id)
        if sf_referrence_id is None:
            return
        for attachment in attachments:
            file_path = attachment.get('path')
            file_name = GCE.asymmetric_decrypt(tip_key, base64.b64decode(attachment.get('name'))).decode()
            file_content = GCE.streaming_encryption_open('DECRYPT', tip_key, file_path)
            client_file_path = os.path.join(file_path, file_name)
            if EXISTING_DOCUMENTS_IN_SF.get(client_file_path):
                # Don't upload attachment if already uploaded
                continue
            body = b''
            read_file = True
            while read_file:
                try:
                    body += file_content.read('rb')
                except TypeError:
                    read_file = False
            body = base64.b64encode(body)
            file_data = {
                'title': file_name,
                'PathOnClient': client_file_path,
                'VersionData': body.decode(),
                'FirstPublishLocationId': sf_referrence_id,
            }
            try:
                self.sf.ContentVersion.create(file_data)
            except SalesforceMalformedRequest as error:
                log.err(error.content)
        return

    def sync_clients_with_sf(self, tip_key, decrypted_answers, gl_answers, itip_id, attachments=[]):
        existing_client_in_sf = self._get_sf_data(self.SF_CLIENT_API_ID)
        sf_client_data = self._get_gl_data(decrypted_answers, gl_answers, existing_client_in_sf, self.client_mapping)
        if itip_id not in existing_client_in_sf:
            self.sync_data_with_sf(self.SF_CLIENT_API_ID, sf_client_data)
        if attachments:
            self.sync_attachments(tip_key, itip_id, self._get_sf_data(self.SF_CLIENT_API_ID), attachments)
        return

    def sync_issues_with_sf(self, tip_key, decrypted_answers, gl_answers, itip_id, attachments=[]):
        existing_issue_in_sf = self._get_sf_data(self.SF_ISSUE_API_ID)
        sf_issue_data = self._get_gl_data(
            decrypted_answers, gl_answers, self._get_sf_data(self.SF_CLIENT_API_ID), self.issue_mapping
        )
        if itip_id not in existing_issue_in_sf:
            self.sync_data_with_sf(self.SF_ISSUE_API_ID, sf_issue_data)
        if attachments:
            self.sync_attachments(tip_key, itip_id, self._get_sf_data(self.SF_ISSUE_API_ID), attachments)
        return

    def sync_data_with_sf(self, SF_API_ID, sf_data):
        try:
            getattr(self.sf, SF_API_ID).create(sf_data)
        except SalesforceMalformedRequest as error:
            log.err(error.message.format(url=error.url, content=error.content))
        return
