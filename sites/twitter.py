from twitter_scraper import (get_tweets, Profile)

class TwitterScraper():

    def __init(self):
        pass

    def getTweets(self, keyword = None, page_size=1):
        if keyword is not None:
            return get_tweets(keyword, pages=page_size)
        return None
    
    def getUserProfile(self, name = None):
        if name is not None:
            profile = Profile(name)
            return profile.to_dict()
        return None