import src.ef_connector as ef_connection
import src.ef_rating as ef_rating
import src.ef_functions as ef_functions
import src.ef_subscription as ef_subscribtion
import os
import threading
import time
import sys
import datetime
from apiclient import errors
import random


class Distribution:
    # Connector instance
    inst_conn = ef_connection.Connector()

    # Hilfsfunktion_yt instance
    inst_helpfct = ef_functions.Hilfsfunktionen_yt()

    # Rating instance
    inst_rating = ef_rating.Rating()

    # Subscription instance
    inst_subscr = ef_subscribtion.Subscription()

    __daytime_factor = None

    def __init__(self):
        pass

    def get_accounts_number(self):

        account_dir = './acc/youtube/credentials'
        accounts = os.listdir(account_dir)
        accounts.sort()

        accounts_number = int(accounts[-1])

        if len(accounts) != accounts_number:
            print(self.inst_helpfct.timestamp() + 'Distribution::get_accounts_number: Attention, number of account'
                  ' directories dont match the max directory number')

        oauth_file = 'oauth2.json'

        for i in accounts:
            oauth_path = account_dir + '/' + str(i) + '/' + oauth_file
            if not os.path.exists(oauth_path):
                print(self.inst_helpfct.timestamp() + 'Distribution::get_accounts_number: Attention, oauth2 file'
                      ' is missing in directory {0} Not yet signed in?'.format(i))

        return accounts_number

    def get_proxy_list(self):

        proxy_array = []

        with open('proxy_socks.txt', mode='r') as file:
            data = file.readlines()
            for line in data:
                line = line.strip('\n')
                line_array = line.split(':')
                proxy_array.append(line_array)

        return proxy_array

    def dynamic_threads_number(self, threads_number_max):

        current_time = datetime.datetime.now().time()

        morning_start = datetime.time(6, 0, 0)
        midday_start = datetime.time(12, 0, 0)
        evening_start = datetime.time(18, 0, 0)
        night_start = datetime.time(0, 0, 0)

        if morning_start <= current_time < midday_start:
            self.__daytime_factor = 0.4
            print(self.inst_helpfct.timestamp() + 'Distribution::dynamic_threads_number: '
                                                  'Daytime Morning was triggered.')
        elif midday_start <= current_time < evening_start:
            self.__daytime_factor = 0.6
            print(self.inst_helpfct.timestamp() + 'Distribution::dynamic_threads_number: '
                                                  'Daytime Midday was triggered.')

        elif night_start > current_time > evening_start or evening_start < current_time > night_start:

            if night_start > current_time > evening_start:
                self.__daytime_factor = 1
                print(self.inst_helpfct.timestamp() + 'Distribution::dynamic_threads_number: '
                                                      'Daytime Evening was triggered.')

            elif evening_start < current_time > night_start:
                self.__daytime_factor = 1
                print(self.inst_helpfct.timestamp() + 'Distribution::dynamic_threads_number: '
                                                      'Daytime Evening was triggered.')

        elif (night_start <= current_time < morning_start) or (night_start <= current_time > morning_start):
            self.__daytime_factor = 0.2
            print(self.inst_helpfct.timestamp() + 'Distribution::dynamic_threads_number: '
                                                  'Daytime Night was triggered.')
        else:
            # To make sure its defined, would work without, but python cant see it.
            print(self.inst_helpfct.timestamp() + 'Distribution::dynamic_threads_number: '
                                                  'Attention, undefined daytime was triggered.')
            self.__daytime_factor = 0.2

        if int(threads_number_max * self.__daytime_factor) == 0:
            # Make sure, at least 1 thread is active.
            return 1
        else:
            return int(threads_number_max * self.__daytime_factor)


class Distribution_yt(Distribution):

    def thread_rating(self, account_nr, proxy_host, proxy_port, proxy_type, auto_video, proxy_user, proxy_pass,
                      stretch_factor, max_history_sites=1, one_shot_channel_id=None, one_shot_video_id=None,
                      one_shot_reason=1, watch_video_settings=1, thread_name=None):

        if one_shot_video_id is not None and one_shot_channel_id is not None:
            sys.exit(self.inst_helpfct.timestamp() + 'Distribution::thread_rating: At least two one'
                                                     ' shot parameters were provided,'
                     ' for channel and video. Pls provide only one parameter at the time.')

        yt_handle = None

        try:
            yt_handle = self.inst_conn.yt_connection(account_nr, proxy_host, proxy_port, proxy_type, proxy_user,
                                                     proxy_pass)
        except errors.HttpError as e:
            print(self.inst_helpfct.timestamp() + 'Distribution::thread_rating: '
                                                  'Something went wrong, yt_handle not created? An HTTP '
                  'error {0} occurred:\n{1}'.format(e.resp.status, e.content))

        if not yt_handle:
            return False

        proxy_info = [proxy_host, proxy_port, proxy_type, proxy_user, proxy_pass]

        #self.inst_helpfct.watch_video('_PmYvOnfcpk', proxy_info)

        # Channel_list_by_id and video_list_by_channel have the same order
        # its needed for Rating.youtube_channel function to verify if to rate up or down
        if one_shot_channel_id is None:
            channel_list_by_id = self.inst_helpfct.get_channel_list_from_sqlite()
        else:
            channel_list_by_id = [[one_shot_channel_id, one_shot_reason]]

        # If just a video is provided, so rate the video.
        if one_shot_video_id is not None:
            rating = None
            if one_shot_reason == 1:
                rating = 'like'
            elif one_shot_reason == 0:
                rating = 'dislike'
            else:
                print(self.inst_helpfct.timestamp() + 'Distribution::thread_rating: '
                                                      'Attention, reason argument is not 1 or 0')
            self.inst_rating.youtube_video_manual(yt_handle, one_shot_video_id, proxy_info, stretch_factor,
                                                  watch_video_settings, rating)
        # If its not the case, than a channel or auto channel from db is wished
        else:
            # print(channel_list_by_id)
            video_list_by_channel = self.inst_helpfct.video_id_list_by_channel(yt_handle, channel_list_by_id,
                                                                               max_history_sites)

            # If auto_video is enabled, then call additional youtube_video_auto function
            # its rating the videos from db
            if auto_video:
                self.inst_rating.youtube_video_auto(yt_handle, proxy_info, stretch_factor,
                                                    watch_video_settings, thread_name)

            # print(video_list_by_channel)
            self.inst_rating.youtube_channel_auto(yt_handle, video_list_by_channel, channel_list_by_id, stretch_factor,
                                                  watch_video_settings, thread_name, proxy_info)

        return True

    def thread_subscription(self, account_nr, proxy_host, proxy_port, proxy_type, proxy_user, proxy_pass,
                            one_shot_subscription):

        yt_handle = None

        try:
            yt_handle = self.inst_conn.yt_connection(account_nr, proxy_host, proxy_port, proxy_type, proxy_user,
                                                     proxy_pass)
        except errors.HttpError as e:
            print(self.inst_helpfct.timestamp() + 'Distribution::thread_subscription: '
                                                  'Something went wrong, yt_handle not created? An HTTP '
                  'error {0} occurred:\n{1}'.format(e.resp.status, e.content))

        try:
            channel_title = self.inst_subscr.add_subscription_yt(yt_handle, one_shot_subscription)
        except errors.HttpError as e:
            print(self.inst_helpfct.timestamp() + "Distribution::thread_subscription: "
                                                  "An HTTP error {0} occurred:\n{1}".format(e.resp.status, e.content))
        else:
            print(self.inst_helpfct.timestamp() + "Distribution::thread_subscription: "
                                                  "A subscription to {0} was added.".format(channel_title))

    def run(self, threads_number_max, stretch_factor, threads_dynamic, accounts_number_to_use,
            max_history_sites, auto_video, one_shot_channel_id, one_shot_video_id_or_link, one_shot_reason,
            one_shot_subscription, proxy_type, watch_video_settings, accounts_number_available, random_accounts):

        # Get proxy list with ports
        proxy_list = self.get_proxy_list()

        thread = None

        # Check and print the mode
        if one_shot_subscription is not None:
            print(self.inst_helpfct.timestamp() + 'Distribution::run: One shot Channel subscription mode was started, '
                                                  'since since channel id as one_shot_subscription was provided')
        elif one_shot_channel_id is None and one_shot_video_id_or_link is None:
            print(self.inst_helpfct.timestamp() + 'Distribution::run: auto-channel-mode was started, '
                                                  'since no one-shot channel or video provided')
        elif one_shot_channel_id is None and one_shot_video_id_or_link is not None:
            print(self.inst_helpfct.timestamp() + 'Distribution::run: one shot video mode was started')
        elif one_shot_channel_id is not None and one_shot_video_id_or_link is None:
            print(self.inst_helpfct.timestamp() + 'Distribution::run: one shot channel mode was started')
        if auto_video and one_shot_subscription is None:
            print(self.inst_helpfct.timestamp() + 'Distribution::run: Additionally auto_video'
                                                  ' (lonely videos from db) was started')

        # First we will fast check if credentials are available for ALL accounts

        broken_account_list = []

        yt_accounts_list = range(1, accounts_number_available + 1)

        for account_nr in yt_accounts_list:
            # Get proxy_host and proxy_port
            proxy_host = proxy_list[account_nr - 1][0]
            proxy_port = proxy_list[account_nr - 1][1]
            proxy_user = None
            proxy_pass = None
            # Check if proxy file has login - pass format and assign the arguments
            if len(proxy_list[account_nr - 1]) == 4:
                proxy_user = proxy_list[account_nr - 1][2]
                proxy_pass = proxy_list[account_nr - 1][3]
            elif len(proxy_list[account_nr - 1]) != 4 and len(proxy_list[account_nr - 1]) != 2:
                raise print(self.inst_helpfct.timestamp() +
                                'Distribution::run: Attention, Proxy file with wrong format??? Quit application')
            # TODO Fix Proxies not reachable
            try:
                valid = self.inst_conn.yt_connection(account_nr, proxy_host, proxy_port, proxy_type,
                                                     proxy_user, proxy_pass)
            except:
                valid = False
                print(self.inst_helpfct.timestamp() +
                            'Distribution::run: Attention, Proxy or account nr. {0} is down?'.format(str(account_nr)))
            if not valid:
                broken_account_list.append(account_nr)
            # try:
            #    self.inst_conn.yt_connection(account_nr, proxy_host, proxy_port, proxy_type, proxy_user, proxy_pass)
            # except:
            #    print('FEHLER FEHLER')
            # time.sleep(10)

        one_shot_video_id = None

        if one_shot_video_id_or_link is not None:
            # Check for a proper video_id, if its a link, extract it from the link
            one_shot_video_id = self.inst_helpfct.get_yt_video_id_from_link(one_shot_video_id_or_link)

            # Check if channel_id and video_id are both provided, if its the case, raise an error, because only
            # one parameter can be passed. As video_id already checked, check for channel_id

            if one_shot_channel_id is not None:
                sys.exit(self.inst_helpfct.timestamp() + 'Distribution::run: '
                                                         'At least two one shot parameters were provided,'
                         ' for channel and video. Pls provide only one parameter at the time.')

        if accounts_number_to_use is None:
            accounts_number_to_use = self.get_accounts_number()

        if accounts_number_to_use > len(proxy_list):
            print(self.inst_helpfct.timestamp() + 'Distribution::run: Attention, '
                                                  'Accounts number is higher than Proxy number.'
                  ' Strange behavior or crash is possible when arguments passed to thread_rating function')

        # Calculate the dynamic threads number if necessary
        if threads_dynamic:
            threads_number_dynamic = self.dynamic_threads_number(threads_number_max)
        else:
            threads_number_dynamic = threads_number_max
        print(self.inst_helpfct.timestamp() + 'Distribution::run: current max'
                                              ' possible threads (dynamic): {0}'.format(threads_number_dynamic))

        if random_accounts:

            # Lets randomize the account list and proxy list in the same way,
            # so not always the first accounts are being used first. 2 Lists are needed so ips are not mixed
            # with different accounts.

            index_shuffle = list(range(len(yt_accounts_list)))
            random.shuffle(index_shuffle)

            yt_accounts_list_shuffle = []
            proxy_list_shuffle = []

            for i in index_shuffle:
                yt_accounts_list_shuffle.append(yt_accounts_list[i])
                proxy_list_shuffle.append(proxy_list[i])

            # Now we get 2 randomized lists in the same way, now lets copy them to original lists
            yt_accounts_list = yt_accounts_list_shuffle
            proxy_list = proxy_list_shuffle
            print(self.inst_helpfct.timestamp() + 'Distribution::run: Attention, randomized account_list and'
                                                  ' proxy_list are being used')
        else:
            pass

        # Now create a handle for each account number and proxy
        # because of the range increase the account number by 1
        for account_nr in yt_accounts_list:

            if account_nr not in broken_account_list:
                # Get proxy_host and proxy_port
                proxy_host = proxy_list[account_nr - 1][0]
                proxy_port = proxy_list[account_nr - 1][1]
                proxy_user = None
                proxy_pass = None
                # Check if proxy file has login - pass format and assign the arguments
                if len(proxy_list[account_nr - 1]) == 4:
                    proxy_user = proxy_list[account_nr - 1][2]
                    proxy_pass = proxy_list[account_nr - 1][3]
                elif len(proxy_list[account_nr - 1]) != 4 and len(proxy_list[account_nr - 1]) != 2:
                    raise print(self.inst_helpfct.timestamp() +
                                'Distribution::run: Attention, Proxy file with wrong format??? Quit application')

                thread_name = 'Thread_' + str(account_nr)
                # No one_shot_subscription means rating

                # thread = None
                if one_shot_subscription is None:
                    thread = threading.Thread(target=self.thread_rating, name=thread_name,
                                              args=(account_nr, proxy_host, proxy_port, proxy_type,
                                                    auto_video, proxy_user, proxy_pass, stretch_factor,
                                                    max_history_sites, one_shot_channel_id, one_shot_video_id,
                                                    one_shot_reason, watch_video_settings, thread_name))
                    thread.start()
                    print(self.inst_helpfct.timestamp() + 'Distribution::run: ' + thread.getName() + ' was started')

                if one_shot_subscription is not None:
                    # Threats are not needed here, we dont need speed, for 500 subscribirs in one day, we need,
                    # just every 180 seconds a new subscriber. We dont run subscription and rating together,
                    # so they are not needed.
                    time.sleep(random.randint(120, 240))
                    self.thread_subscription(account_nr, proxy_host, proxy_port, proxy_type,
                                             proxy_user, proxy_pass, one_shot_subscription)

                number_of_threads = len(threading.enumerate())

                # For some reason we have to slow down threads starting, or we will get different ssl errors
                # Additionally it prevents to open new browser window while the other still logs in
                # should be at least 30 seconds.
                time.sleep(random.randrange(35, 60))

                # Check how many threads are currently running
                # Minus 1 is needed, because main thread is counted as well

                while number_of_threads - 1 > threads_number_dynamic:
                    sleeping_time = 300
                    print(self.inst_helpfct.timestamp() + 'Distribution::run: Max number of threads is reached.'
                                                          ' Wait {0} seconds for some threads to finish before'
                                                          ' new assignment. Current'
                                                          ' active threads are {1}'.format(sleeping_time,
                                                                                           threading.enumerate()))
                    time.sleep(sleeping_time)
                    number_of_threads = len(threading.enumerate())
            else:
                print(self.inst_helpfct.timestamp() + 'Distribution::run: Account nr. {0} was initially broken, '
                                                      'thread for this account skipped'.format(account_nr))
                pass

        # Wait till all threads are finished before continue
        print(self.inst_helpfct.timestamp() + 'Distribution::run: Threads join point is reached by Main Thread, '
                                              'waiting for {0} threads to'
                                              ' finish'.format(len(threading.enumerate()) - 1))
        thread.join()
        print(self.inst_helpfct.timestamp() + 'Distribution::run: Threads join point was passed, threads are all'
                                              ' finished for this run')

        print(self.inst_helpfct.timestamp() + 'Distribution::run: Main thread finished')
