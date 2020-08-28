from sites.twitter import TwitterScraper
from flask import(
    Flask,
    request,
    jsonify,
)

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/twitter"

def convertItem(tweet):
    temp = {}
    temp['name'] = tweet.name
    temp['tweet'] = tweet.tweet
    temp['link'] = tweet.link
    temp['replies_count'] = tweet.replies_count
    temp['retweets_count'] = tweet.retweets_count
    temp['likes_count'] = tweet.likes_count
    temp['datestamp'] = tweet.datestamp
    temp['timestamp'] = tweet.timestamp
    temp['timezone'] = tweet.timezone
    return temp    

@app.route("/user", methods=["GET", "POST"])
def getUserTweets():
    user = request.args.get('name')
    if user is None:
        return 200
    size = request.args.get('size')
    if size is None:
        size = 200   
    keyword = request.args.get('keywords')       
    twitter = TwitterScraper()
    ret = twitter.get_user_tweets(user, keyword, size)
    tweets = []
    for tweet in ret:
        tweets.append(convertItem(tweet)) 
    return jsonify(tweets), 200

@app.route("/tweets", methods=["GET", "POST"])
def getTweets():
    keyword = request.args.get('keywords')
    if keyword is None:
        return 200
    page_size = request.args.get('page')
    if page_size is None:
        page_size = 3
       
    twitter = TwitterScraper()
    ret = twitter.getTweets(keyword, size=int(page_size))
    tweets = []
    for tweet in ret:
        tweets.append(convertItem(tweet)) 
    return jsonify(tweets), 200

@app.route("/profile", methods=["GET", "POST"])
def getProfile():
    name = request.args.get('name')
    if name is None:
        return 200
    twitter = TwitterScraper()
    ret = twitter.getUserProfile(name)
    return jsonify(ret), 200    

@app.route("/")
def index():
    return 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True,
            port=7778, debug=True)
