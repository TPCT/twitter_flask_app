from flask import Blueprint
from Controllers.DashboardController import index

DashboardBluePrint = Blueprint('dashboard', __name__)
DashboardBluePrint.route('/', methods=['GET'])(index)
