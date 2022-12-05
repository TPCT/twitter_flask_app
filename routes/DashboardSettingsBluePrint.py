from flask import Blueprint
from Controllers.DashboardSettingsController import index, store

DashboardSettingsBluePrint = Blueprint('dashboard_settings', __name__)
DashboardSettingsBluePrint.route('/')(index)
DashboardSettingsBluePrint.route('/store', methods=['POST'])(store)
