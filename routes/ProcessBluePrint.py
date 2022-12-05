from flask import Blueprint
from Controllers.ProcessController import store, delete

ProcessBluePrint = Blueprint('process', __name__)
ProcessBluePrint.route('/process/start/<int:session_id>')(store)
ProcessBluePrint.route('/process/stop/<int:session_id>')(delete)
