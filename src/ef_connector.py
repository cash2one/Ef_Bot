from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from apiclient import discovery
import os
import src.ef_functions as ef_functions
import src.ef_tools_mod as ef_tools_mod
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ErrorInResponseException

import socks
import random

import httplib2
import time
import subprocess
import threading


class Connector:

    __http_token = None
    driver = None
    thread = None

    def __init__(self):

        # Hilfsfunktion_yt instance
        self.inst_helpfct = ef_functions.Hilfsfunktionen_yt()


    def yt_login_automation(self, account_nr, authorize_url, proxy_host, proxy_port,
                            proxy_type, proxy_user, proxy_pass):

        self.driver = None
        # Change custom default proxy settings to default settings
        # Attention, prevent any rating during this time, since no proxy is used
        socks.setdefaultproxy()

        account_info = self.inst_helpfct.yt_get_account_info('gmail', account_nr)

        import src.ef_distribution as distr

        proxy_list = distr.Distribution().get_proxy_list()

        browser = 'Firefox'

        if browser == 'Chrome':
            self.driver = self.inst_helpfct.install_chrome_proxy(proxy_list[account_nr-1][0], proxy_list[account_nr-1][1])

        if browser == 'Firefox':
            self.driver = self.inst_helpfct.install_firefox_proxy_new(proxy_list[account_nr-1][0], proxy_list[account_nr-1][1])

        #self.driver.set_script_timeout(20)
        #self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(15)

        self.driver.get(authorize_url)
        time.sleep(random.randrange(5, 8))
        if browser == 'Firefox':
            self.driver.maximize_window()

        # Now perform log in tasks
        self.driver.find_element_by_id('Email').send_keys(account_info['Email'])
        time.sleep(random.randrange(5, 8))

        self.driver.find_element_by_id('next').click()
        time.sleep(random.randrange(5, 8))

        self.driver.find_element_by_id('Passwd').send_keys(account_info['Password'])
        time.sleep(random.randrange(5, 8))

        self.driver.find_element_by_id('signIn').click()
        time.sleep(random.randrange(5, 8))

        approve_button = len(self.driver.find_elements_by_id('submit_approve_access'))
        challenge_picker = len(self.driver.find_elements_by_id('challengePickerList'))
        phone_number = len(self.driver.find_elements_by_name('phoneNumber'))
        time.sleep(random.randrange(8, 12))

        if approve_button == 1:
            try:
                # subprocess.call(["xdotool", "mousemove", "1128", "420"])
                # subprocess.call(["xdotool", "click", "1"])

                self.driver.find_element_by_id('submit_approve_access').click()
                time.sleep(random.randrange(5, 8))

                # Threads are not working for Firefox? Works only for Chrome, but Chrome does not return
                # valid oauth2 file. Everything is a big mess here. :-( Addionally, Firefox hangs when using
                # Selenium after pushing Approve button, thats why I tried with threads.
                # Using the mouse for clicking works, but no valid Oauth2 file :-(

                # self.thread = threading.Thread(target=self.driver.
                #                               find_element_by_id('submit_approve_access').click()).start()

                # time.sleep(random.randrange(5, 8))
                # subprocess.call(["xdotool", "mousemove", "1907", "12"])
                # time.sleep(random.randrange(5, 8))
                # subprocess.call(["xdotool", "click", "1"])

            finally:

                self.driver.quit()
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port),
                                      username=proxy_user, password=proxy_pass)
                socks.wrapmodule(httplib2)

        elif challenge_picker == 1:
            print(self.inst_helpfct.timestamp() + 'Connector::yt_automation:'
                                                  ' Aditional verification for account'
                                                  ' Nr. {0} needed'.format(account_nr))
            with open('log.log', 'a') as file:
                file.write(self.inst_helpfct.timestamp() + 'Connector::yt_automation:'
                                                  ' Additional verification for account'
                                                  ' Nr. {0} needed\n'.format(account_nr))

            self.driver.find_element_by_xpath("(//BUTTON[@type='submit'])[3]").click()
            time.sleep(random.randrange(5, 8))
            self.driver.find_element_by_name('phoneNumber').send_keys(account_info['Phone_Number'])
            time.sleep(random.randrange(5, 8))
            self.driver.find_element_by_id('submit').click()
            time.sleep(random.randrange(15, 20))

            account_disabled = len(self.driver.find_elements_by_xpath("//DIV[@class='LJtPoc RjeAfc']"))

            if account_disabled == 0:
                time.sleep(random.randrange(5, 8))
                self.driver.find_element_by_id('submit_approve_access').click()
            else:
                time.sleep(random.randrange(5, 8))
                with open('log.log', 'a') as file:
                    file.write(self.inst_helpfct.timestamp() + 'Connector::yt_automation:'
                                                               ' Account'
                                                               ' Nr. {0} disabled\n'.format(account_nr))

            self.driver.quit()
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port),
                                  username=proxy_user, password=proxy_pass)
            socks.wrapmodule(httplib2)

        elif phone_number == 1:

            time.sleep(random.randrange(5, 8))
            self.driver.find_element_by_name('phoneNumber').send_keys(account_info['Phone_Number'])
            time.sleep(random.randrange(5, 8))
            self.driver.find_element_by_id('submit').click()
            time.sleep(random.randrange(8, 12))

            self.driver.find_element_by_id('submit_approve_access').click()
            time.sleep(random.randrange(5, 8))

            self.driver.quit()
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port),
                                  username=proxy_user, password=proxy_pass)
            socks.wrapmodule(httplib2)


        else:
            time.sleep(random.randrange(5, 8))
            print(self.inst_helpfct.timestamp() + 'Connector::yt_automation:'
                                                  ' Approve button for account Nr. {0} not found'.format(account_nr))
            time.sleep(random.randrange(5, 8))
            self.driver.quit()

            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port),
                                  username=proxy_user, password=proxy_pass)

            socks.wrapmodule(httplib2)


        # Different approach for a mouse click
        #subprocess.call(["xdotool", "mousemove", "1128", "420"])
        #subprocess.call(["xdotool", "click", "1"])



    def yt_connection(self, account_nr, proxy_host, proxy_port, proxy_type, proxy_user, proxy_pass):

        if (proxy_user or proxy_pass) is None:
            proxy_user = 'EUR233698'
            proxy_pass = 'KS5yfdvh4T'

        sub_dir = "./acc/youtube/credentials/{0}/".format(str(account_nr))

        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)

        CLIENT_SECRETS_FILE = "./acc/youtube/client_secrets.json"
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
            self.__http_token = httplib2.Http()

            """
            import urllib3

            http = urllib3.PoolManager()
            http.headers['user_name'] = 'your_name'
            http.headers['password'] = 'your_pass'

            self.__http_token = http
            """
            """
            proxies = {'http': 'socks5://45.63.89.33:6789'}
            s = requests.Session()
            s.proxies.update(proxies)
            self.__http_token = s
            """

            # Not working
            # Old implementation, its not working with httplib2, since ProxyInfo is only working with python2
            # self.__http_token = httplib2.Http(proxy_info=httplib2.
            # ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_SOCKS5,
            # proxy_host=proxy_host, proxy_port=proxy_port,
            # proxy_user=proxy_user, proxy_pass=proxy_pass))

        # ###################################################################################################
        # Attention, only socks5 is working with httplib2, read https://pypi.python.org/pypi/PySocks/1.6.6
        # ###################################################################################################
        elif proxy_type == 'http':



            #socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, proxy_host, int(proxy_port),
            #                      username=proxy_user, password=proxy_pass)
            #socks.wrapmodule(httplib2)
            #self.__http_token = httplib2.Http()

            # Not working, ProxyInfo only for Python 2
            self.__http_token = httplib2.Http(proxy_info=httplib2.
                                              ProxyInfo(proxy_type=httplib2.socks.PROXY_TYPE_HTTP,
                                                        proxy_host=proxy_host, proxy_port=int(proxy_port),
                                                        proxy_user=proxy_user, proxy_pass=proxy_pass))

        else:
            raise Exception(self.inst_helpfct.timestamp() + 'Connector::yt_connection: Wrong proxy_type passed')

        if credentials is None or credentials.invalid:
            print(self.inst_helpfct.timestamp() + 'Connector::yt_connection: No credentials, running authentication'
                                                  ' flow to get OAuth token')
            print(self.inst_helpfct.timestamp() + 'Connector::yt_connection: Account Nr. {0} not found or'
                                                  ' credentials invalid'.format(account_nr))

            credentials = ef_tools_mod.run_flow(flow, storage, account_nr, proxy_host,
                                   proxy_port, proxy_type, proxy_user,
                                   proxy_pass, flags=None, http=self.__http_token)
        else:
            print(self.inst_helpfct.timestamp() + 'Connector::yt_connection:'
                                                  ' Account Nr. {0} credentials accepted'.format(account_nr))

        if credentials is None or credentials.invalid:
            print(self.inst_helpfct.timestamp() + 'Something went wrong with account Nr. {0} credentials'
                                                  ' not correct'.format(account_nr))
            with open('log.log', 'a') as file:
                file.write(self.inst_helpfct.timestamp() + 'Connector::yt_connection:'
                                                           ' Account {0} was not accepted.\n'.format(account_nr))
            return False

        return discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                               http=credentials.authorize(self.__http_token))
