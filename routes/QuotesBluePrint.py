from flask import Blueprint
from Controllers.QuotesController import store, delete

QuotesBluePrint = Blueprint('quotes', __name__)
QuotesBluePrint.route('/store', methods=['POST'])(store)
QuotesBluePrint.route('/delete', methods=['POST'])(delete)
