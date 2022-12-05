from flask import Blueprint
from Controllers.RepliesController import store, delete

RepliesBluePrint = Blueprint('replies', __name__)
RepliesBluePrint.route('/store', methods=['POST'])(store)
RepliesBluePrint.route('/delete', methods=['POST'])(delete)
