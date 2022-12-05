from flask import Blueprint
from Controllers.SettingsController import store

SettingsBluePrint = Blueprint('settings', __name__)
SettingsBluePrint.route('/store/<int:session_id>', methods=['POST'])(store)
