from flask import Blueprint
from Controllers.UsersController import index, store, delete

UsersBluePrint = Blueprint('users', __name__)
UsersBluePrint.route('/')(index)
UsersBluePrint.route('/store', methods=['POST'])(store)
UsersBluePrint.route('/delete/<int:account_id>', methods=['POST'])(delete)
