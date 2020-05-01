SitesAvailable = [
    {
        'name':'youtube',
        'thread_pool_size' : 1,
        'search_url':'https://www.youtube.com/results?search_query=',
    },
    {
        'name':'pornhub',
        'thread_pool_size' : 1,
        'search_url':'https://cn.pornhub.com/video/search?search=',
    }
]

def findAvailableSiteConfigure(name):
    for site in SitesAvailable:
        if site['name'] == name:
            return site 
    return None        
