from sites.twitter import TwitterScraper
from flask import(
    Flask,
    request,
    jsonify,
)

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/twitter"

@app.route("/tweets", methods=["GET", "POST"])
def getTweets():
    keyword = request.args.get('keywords')
    if keyword is None:
        return 200
    page_size = request.args.get('page')
    if page_size is None:
        page_size = 3
    
    twitter = TwitterScraper()
    ret = twitter.getTweets(keyword, page_size=int(page_size))
    tweets = []
    for tweet in ret:
        tweets.append(tweet)
    
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
