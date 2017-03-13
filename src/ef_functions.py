import sqlite3
import urllib.parse
import random
import time
import datetime


class Hilfsfunktionen:

    # Return a timestamp for output
    def timestamp(self):
        return str('{:%d-%m-%Y %H:%M:%S}: '.format(datetime.datetime.now()))

    # Return true if x is in the range [start, end]
    def time_in_range(self, start_time, end_time, current_time):
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            return start_time <= current_time or current_time <= end_time

    # Check if its "sleep" time or not, to simulate a human
    # To improve the results, include timezone check for a certain ip
    def time_function(self, turned_on=True):

        if turned_on:
            current_time = datetime.datetime.now().time()
            # Randomize a bit, so the threads don't 'collapse' all at the same time
            start_time = datetime.time(random.randint(6, 8), 0, 0)
            end_time = datetime.time(random.randint(21, 23), 0, 0)

            # If time in range leave the loop and continue with the code
            while not self.time_in_range(start_time, end_time, current_time):
                print(self.timestamp() + "Hilfsfunktionen::time_function: In a loop, reason: Sleeping time :-)")
                print(self.timestamp() + "Hilfsfunktionen::time_function: current time: " + str(current_time))
                time.sleep(1000)
                current_time = datetime.datetime.now().time()
            else:
                # Don't be to fast, simulate a human
                time.sleep(random.randint(30, 300))
        else:
            print(self.timestamp() + "Hilfsfunktionen::time_function: Attention, time_function is turned off")
            # Don't be to fast, simulate a human
            time.sleep(random.randint(30, 300))

        return True


class Hilfsfunktionen_yt(Hilfsfunktionen):

    # Some statistics on Videos, returns a dictionary with statistics
    @staticmethod
    def video_statistics_by_video_id(yt_handle, yt_video_id):

        result = yt_handle.videos().list(part='contentDetails', id=yt_video_id).execute()
        content_details = result['items'][0]['contentDetails']

        result = yt_handle.videos().list(part='statistics', id=yt_video_id).execute()
        statistics = result['items'][0]['statistics']
        statistics['duration'] = content_details['duration']

        return statistics

    # Youtube id parser by
    # http://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
    # extracts youtube video id, modified by me
    @classmethod
    def get_yt_video_id_from_link(cls, yt_link):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """

        query = urllib.parse.urlparse(yt_link)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urllib.parse.parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail? return yt_link, because it can be all ready an id
        return yt_link

    # Return a list of all channels and their reasons from sqlite db
    def get_channel_list_from_sqlite(self):
        conn = sqlite3.connect('ef_bot.sqlite')
        db_handle = conn.cursor()
        db_handle.execute('select channel_id, reason from yt_channel order by priority asc')

        return db_handle.fetchall()

    @classmethod
    def get_video_list_from_sqlite(cls):
        conn = sqlite3.connect('ef_bot.sqlite')
        db_handle = conn.cursor()
        db_handle.execute('select video_id, reason from yt_video order by priority asc')

        return db_handle.fetchall()

    # Returns Id for Upload section of a certain yt channel
    @classmethod
    def upload_id_from_channel_id(cls, yt_handle, yt_channel_id):
        id_list = yt_handle.channels().list(part='contentDetails', id=yt_channel_id).execute()
        return id_list['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Returns a list with all videos in upload folder of a certain channel, limited to a number of sites
    # This function is needed for the function video_id_list_by_channel
    def video_id_list_from_upload_id(self, yt_handle, upload_id, max_sites=201):
        id_list = yt_handle.playlistItems().list(part='snippet', playlistId=upload_id).execute()
        total_results = id_list['pageInfo']['totalResults']
        results_per_page = id_list['pageInfo']['resultsPerPage']
        next_page_token = id_list['nextPageToken']

        # check how many pages are available
        number_of_pages = 0
        try:
            number_of_pages = total_results // results_per_page
        except ZeroDivisionError as detail:
            print(self.timestamp() + 'Division durch 0!!!', detail)

        if number_of_pages == 0:
            number_of_pages = 1

        # Create an item list and append the first page
        item_list = []
        for i in id_list['items']:
            item_list.append(i)

        # Add results to the list, if more than 1 sites requested
        j = 1
        if max_sites > 1:
            while j < number_of_pages:
                id_list = yt_handle.playlistItems().list(part='snippet', playlistId=upload_id,
                                                         pageToken=next_page_token).execute()
                for i in id_list['items']:
                    item_list.append(i)
                next_page_token = id_list['nextPageToken']
                j += 1
                # Max 1000 Videos if 201 sites * 5
                if j == max_sites:
                    break

        # Now create a list with all video ids
        video_id_list = []
        i = 0
        while i < len(item_list):
            video_id_list.append(item_list[i]['snippet']['resourceId']['videoId'])
            i += 1

        return video_id_list

    # Returns a video list by id, it depends on function: video_id_list_from_upload_id
    def video_id_list_by_channel(self, yt_handle, channel_id_list, max_sites=1):

        video_id_list_by_channel = []
        # Channel reason is not used??? How we know if to like or dislike?
        for channel_tuple in channel_id_list:
            # Get upload_id for the channel
            upload_id = self.upload_id_from_channel_id(yt_handle, channel_tuple[0])
            # Get the video list for the upload page
            video_id_list_by_channel.append(self.video_id_list_from_upload_id(yt_handle, upload_id, max_sites))

        return video_id_list_by_channel
