import base64
from email.mime.text import MIMEText

import httplib2
import os

from apiclient import discovery
from googleapiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class EmailNotification:
    def __init__(self, scope='https://www.googleapis.com/auth/gmail.send', client_secret_file='client_secret.json',
                 application_name='SocialCube', credential_dir='.credentials', credential_file='credential.json'):
        self.SCOPES = scope
        self.CLIENT_SECRET_FILE = client_secret_file
        self.APPLICATION_NAME = application_name
        self.credential_dir = credential_dir
        self.credential_file = credential_file
        self.message = None
        self.service = None

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        self.credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(self.credential_dir):
            os.makedirs(self.credential_dir)
        credential_path = os.path.join(self.credential_dir, self.credential_file)
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def create_message(self, to, subject, message_text, sender='me'):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        self.message = {'raw': base64.urlsafe_b64encode(message.as_string())}

    def send_message(self, message, user_id='me'):
        """Send an email message.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print 'Message Id: %s' % message['id']
            return message
        except errors.HttpError, error:
            print 'An error occurred: %s' % error

    def send_email(self, to, subject, content):
        """Shows basic usage of the Gmail API.

        Creates a Gmail API service object and outputs a list of label names
        of the user's Gmail account.
        """
        self.build_service()

        self.create_message(to, subject, content)
        result = self.send_message(self.message)
        return result

    def build_service(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)


def email(to='lunanli3@illinois.edu', subject='Taxongen job finished',
          content='Please check the result on server at /shared/data/lunanli3/local-embedding/taxonomies/our-tweets.txt. Thanks.\n Best,\nLunan Li',
          scope='https://www.googleapis.com/auth/gmail.send', client_secret_file='client_secret.json',
          application_name='SocialCube', credential_dir='~/.credentials', credential_file='credential.json'):
    en = EmailNotification(scope, client_secret_file, application_name, credential_dir, credential_file)
    en.send_email(to, subject, content)


if __name__ == '__main__':
    email()
