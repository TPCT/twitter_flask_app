from flask import Blueprint
from Controllers.ProxiesController import store, delete

ProxiesBluePrint = Blueprint('proxies', __name__)
ProxiesBluePrint.route('/store/<proxy_for>', methods=['POST'])(store)
ProxiesBluePrint.route('/delete/<proxy_for>', methods=['POST'])(delete)
