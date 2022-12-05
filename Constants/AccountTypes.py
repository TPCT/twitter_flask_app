class AccountTypes:
    tweet = 1
    retweet = 2
    reply = 4
    react = 8
    quote = 16
    checker = 32
    follower = 64
    followed = 128
    profile = 256
    private = 512

    PERMISSIONS = {
        'Tweet': tweet,
        'Retweet': retweet,
        'Reply': reply,
        'React': react,
        'Quote': quote,
        'Checker': checker,
        'Follower': follower,
        'Followed': followed,
        'Profile': profile,
        'Private': private
    }

    @staticmethod
    def getAccountType(permission):
        return AccountTypes.PERMISSIONS.get(permission)

    @staticmethod
    def getAll(without=None):
        if without is None:
            without = []
        permissions = list(AccountTypes.PERMISSIONS.values())
        for permission in without:
            permissions.remove(permission) if permission in permissions else None

        return permissions

    @staticmethod
    def getAllPermissionsNames(without=None):
        if without is None:
            without = []
        return [name for name, value in AccountTypes.PERMISSIONS.items() if value not in without]