from flask import Blueprint
from Controllers.FollowController import index, store, deleteAccount, deleteToBeFollowed, deleteFollowers, download, \
    process, deleteFailed, check

FollowBluePrint = Blueprint('follow', __name__)
FollowBluePrint.route('/')(index)
FollowBluePrint.route('/store/<int:session_id>', methods=['POST'])(store)
FollowBluePrint.route('/accounts/delete/<int:account_id>', methods=['POST'])(deleteAccount)
FollowBluePrint.route('/accounts/followers/delete', methods=['POST'])(deleteFollowers)
FollowBluePrint.route('/accounts/followed/delete', methods=['POST'])(deleteToBeFollowed)
FollowBluePrint.route('/accounts/failed/delete', methods=['POST'])(deleteFailed)
FollowBluePrint.route('/accounts/download')(download)
FollowBluePrint.route('/process')(process)
FollowBluePrint.route('/check')(check)