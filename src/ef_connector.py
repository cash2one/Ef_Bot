from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow

from apiclient import discovery
import os
import httplib2
import time
import src.ef_functions as ef_functions

import socks

class Connector:

    http_token = None

    def __init__(self):

        # Hilfsfunktion_yt instance
        self.inst_helpfct = ef_functions.Hilfsfunktionen_yt()

    def yt_keyboard_and_mouse_login_automation(self):
        a = 0

    def yt_connection(self, account_nr, proxy_host, proxy_port, proxy_type, proxy_user='proxyfish260',
                      proxy_pass='bicedt3352'):

        sub_dir = "./acc/{0}/".format(str(account_nr))

        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        CLIENT_SECRETS_FILE = "client_secrets.json"
        OAUTH_TOKEN_FILE = sub_dir + "oauth2.json"

        YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                       message="Missing client_secrets.json",
                                       scope=YOUTUBE_READ_WRITE_SCOPE)
        storage = Storage(OAUTH_TOKEN_FILE)
        credentials = storage.get()

        if proxy_type == 'socks5':
            # https://github.com/jcgregorio/httplib2/issues/205
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port),
                                  username=proxy_user, password=proxy_pass)
            socks.wrapmodule(httplib2)
            self.http_token = httplib2.Http()

            # Old implementation, its not working with httplib2, since ProxyInfo is only working with python2
            # self.http_token = httplib2.Http(proxy_info=httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_SOCKS5,
            # proxy_host=proxy_host, proxy_port=proxy_port,
            # proxy_user=proxy_user, proxy_pass=proxy_pass))

        # ###################################################################################################
        # Attention, only socks5 is working with httplib2, read https://pypi.python.org/pypi/PySocks/1.6.6
        # ###################################################################################################
        elif proxy_type == 'http':

            socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_host, int(proxy_port),
                                  username=proxy_user, password=proxy_pass)
            socks.wrapmodule(httplib2)
            self.http_token = httplib2.Http()

            # self.http_token = httplib2.Http(proxy_info=httplib2.ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                                                                          #proxy_host=proxy_host, proxy_port=proxy_port))

        else:
            raise Exception(self.inst_helpfct.timestamp() + 'Connector::yt_connection: Wrong proxy_type passed')

        if credentials is None or credentials.invalid:
            print(self.inst_helpfct.timestamp() + 'Connector::yt_connection: No credentials, running authentication'
                                                  ' flow to get OAuth token')
            print(self.inst_helpfct.timestamp() + 'Connector::yt_connection: Account Nr. {0} not found or'
                                                  ' credentials invalid'.format(account_nr))
            credentials = run_flow(flow, storage, flags=None, http=self.http_token)
            time.sleep(5)
        else:
            print(self.inst_helpfct.timestamp() + 'Account Nr. {0} credentials were accepted'.format(account_nr))

        return discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(self.http_token))
