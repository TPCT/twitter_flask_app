from flask import Blueprint
from Controllers.AuthController import index, logout, install

AuthBluePrint = Blueprint('auth', __name__)
AuthBluePrint.route('/', methods=['GET', 'POST'])(index)
AuthBluePrint.route('/logout', methods=['GET'])(logout)
AuthBluePrint.route('/install', methods=['GET'])(install)
