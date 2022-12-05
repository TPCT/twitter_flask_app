from flask import Blueprint
from Controllers.ProfileController import index, store, deleteAccount, deleteAccounts, download, \
    process, deleteCoverImages, deleteBio, deleteProfileImages, deleteProfileNames, deleteProfileCountries

ProfileBluePrint = Blueprint('profile', __name__)
ProfileBluePrint.route('/')(index)
ProfileBluePrint.route('/store/<int:session_id>', methods=['POST'])(store)
ProfileBluePrint.route('/accounts/delete/<int:account_id>', methods=['POST'])(deleteAccount)
ProfileBluePrint.route('/accounts/delete', methods=['POST'])(deleteAccounts)
ProfileBluePrint.route('/profile_cover/delete', methods=['POST'])(deleteCoverImages)
ProfileBluePrint.route('/profile_pictures/delete', methods=['POST'])(deleteProfileImages)
ProfileBluePrint.route('/profile_bios/delete', methods=['POST'])(deleteBio)
ProfileBluePrint.route('/profile_names/delete', methods=['POST'])(deleteProfileNames)
ProfileBluePrint.route('/profile_countries/delete', methods=['POST'])(deleteProfileCountries)
ProfileBluePrint.route('/accounts/download')(download)
ProfileBluePrint.route('/process')(process)