from twitter_scraper import (get_tweets, Profile)
import twint


class TwitterScraper():

    def __init(self):
        pass

    def getTweets(self, keyword=None, size=3):
        if keyword is not None:
            c = twint.Config()
            c.Search = keyword
            c.Store_object = True
            c.Store_json = True
            c.Limit = size*20
            twint.run.Search(c)
            target_items = twint.output.tweets_list
        return target_items

    def getUserProfile(self, name=None):
        if name is not None:
            c = twint.Config()
            c.Username = name
            c.Store_object = True
            c.Store_json = True
            c.Limit = 10
            twint.run.Search(c)
            twint.run.Profile(c)
            twint.output
        return None

    def get_user_tweets(self, name=None, keyword=None, size=200):
        if name is not None:
            c = twint.Config()
            c.Username = name
            c.Search = keyword
            c.Store_object = True
            c.Store_json = True
            c.Limit = size
            # Run
            twint.run.Search(c)
            target_items = twint.output.tweets_list
        return target_items
