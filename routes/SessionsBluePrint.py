from flask import Blueprint
from Controllers.SessionsController import store, delete, select

SessionsBluePrint = Blueprint('sessions', __name__)
SessionsBluePrint.route('/store', methods=['POST'])(store)
SessionsBluePrint.route('/delete/<int:session_id>')(delete)
SessionsBluePrint.route('/select/<int:session_id>')(select)
