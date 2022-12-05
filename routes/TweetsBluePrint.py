from flask import Blueprint
from Controllers.TweetsController import index, store, deleteTweets, process, deleteAccount, deleteAccounts, download

TweetsBluePrint = Blueprint('tweets', __name__)
TweetsBluePrint.route('/')(index)
TweetsBluePrint.route('/store', methods=['POST'])(store)
TweetsBluePrint.route('/delete/tweets', methods=['POST'])(deleteTweets)
TweetsBluePrint.route('/delete/accounts', methods=['POST'])(deleteAccounts)
TweetsBluePrint.route('/delete/account/<int:account_id>', methods=['POST'])(deleteAccount)
TweetsBluePrint.route('/download/accounts')(download)
TweetsBluePrint.route('/process')(process)
