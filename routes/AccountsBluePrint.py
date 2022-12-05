from flask import Blueprint
from Controllers.AccountsController import index, store, delete, bulkDelete, download

AccountsBluePrint = Blueprint('accounts', __name__)
AccountsBluePrint.route('/')(index)
AccountsBluePrint.route('/store', methods=['POST'])(store)
AccountsBluePrint.route('/delete/<int:account_id>', methods=['POST'])(delete)
AccountsBluePrint.route('/bulkDelete', methods=['POST'])(bulkDelete)
AccountsBluePrint.route('/download')(download)
