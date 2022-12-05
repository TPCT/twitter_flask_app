from flask import Blueprint
from Controllers.CheckerController import index, store, download

CheckerBluePrint = Blueprint('checker', __name__)
CheckerBluePrint.route('/', methods=['GET'])(index)
CheckerBluePrint.route('/download')(download)
CheckerBluePrint.route('/store', methods=['POST'])(store)
