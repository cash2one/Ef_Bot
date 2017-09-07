import src.ef_functions as ef_functions

class Subscription:

    # Hilfsfunktion instance
    inst_helpfct = ef_functions.Hilfsfunktionen_yt()

    def __init__(self):
        pass

    # This method calls the API's youtube.subscriptions.insert method to add a
    # subscription to the specified channel.
    # got and modified the code from https://github.com/youtube/api-samples/blob/master/python/add_subscription.py
    def add_subscription_yt(self, youtube_handle, channel_id):
        # Since this function is primitive and is always in a loop of other functions,
        # we have to delay the response time to simulate a human. So call a
        # time_function here from ef_functions. Don't do this in other auto functions,
        # since you will get 2 delays.
        if self.inst_helpfct.time_function():
            add_subscription_response = youtube_handle.subscriptions().insert(part='snippet', body=dict(
                snippet=dict(resourceId=dict(channelId=channel_id)))).execute()

            return add_subscription_response["snippet"]["title"]

