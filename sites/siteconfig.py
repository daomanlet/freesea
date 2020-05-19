SitesAvailable = [
    {
        'name':'youtube',
        'thread_pool_size' : 1,
        'search_url':'https://www.youtube.com/results?search_query=',
        'video_url' : 'https://www.youtube.com/watch?v=',
        'max_download':3
    },
    {
        'name':'pornhub',
        'thread_pool_size' : 1,
        'search_url':'https://cn.pornhub.com/video/search?search=',
        'video_url' :'https://cn.pornhub.com/view_video.php?viewkey=',
        'max_download':2
    }
]

def findAvailableSiteConfigure(name):
    for site in SitesAvailable:
        if site['name'] == name:
            return site 
    return None        
