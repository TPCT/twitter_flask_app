from flask import Blueprint
from Controllers.ReactionsController import index, download, deleteAccount, deleteAccounts

ReactionsBluePrint = Blueprint('reactions', __name__)
ReactionsBluePrint.route('/')(index)
ReactionsBluePrint.route('/accounts/download')(download)
ReactionsBluePrint.route('/accounts/delete/<int:account_id>', methods=['POST'])(deleteAccount)
ReactionsBluePrint.route('/accounts/delete', methods=['POST'])(deleteAccounts)