from routes.AuthBluePrint import AuthBluePrint
from routes.DashboardBluePrint import DashboardBluePrint
from routes.SessionsBluePrint import SessionsBluePrint
from routes.AccountsBluePrint import AccountsBluePrint
from routes.ProxiesBluePrint import ProxiesBluePrint
from routes.ProcessBluePrint import ProcessBluePrint
from routes.ProfileBluePrint import ProfileBluePrint
from routes.TweetsBluePrint import TweetsBluePrint
from routes.QuotesBluePrint import QuotesBluePrint
from routes.RepliesBluePrint import RepliesBluePrint
from routes.SettingsBluePrint import SettingsBluePrint
from routes.ReactionsBluePrint import ReactionsBluePrint
from routes.FollowBluePrint import FollowBluePrint
from routes.CheckerBluePrint import CheckerBluePrint
from routes.DashboardSettingsBluePrint import DashboardSettingsBluePrint
from routes.UsersBluePrint import UsersBluePrint

blueprints = [
    AuthBluePrint, DashboardBluePrint, SessionsBluePrint, AccountsBluePrint, ProxiesBluePrint, ProcessBluePrint,
    ProfileBluePrint, TweetsBluePrint, QuotesBluePrint, RepliesBluePrint, SettingsBluePrint, ReactionsBluePrint,
    FollowBluePrint, CheckerBluePrint, DashboardSettingsBluePrint, UsersBluePrint
]
authentication_required = [blueprint for blueprint in blueprints if blueprint != AuthBluePrint]
session_required = [blueprint for blueprint in blueprints if blueprint not in
                    [UsersBluePrint, AuthBluePrint, DashboardBluePrint, SessionsBluePrint, DashboardSettingsBluePrint]]
admin_required = [UsersBluePrint]