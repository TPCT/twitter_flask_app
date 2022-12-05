from Models.BaseModel import BaseModel
from Models.SessionModel import SessionModel
from config import db


class ProxyModel(db.Model, BaseModel):
    __tablename__ = "proxies"
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    proxy_user = db.Column(db.VARCHAR(255))
    proxy_password = db.Column(db.VARCHAR(255))
    proxy_ip = db.Column(db.VARCHAR(255))
    proxy_port = db.Column(db.VARCHAR(255))
    proxy_for = db.Column(db.VARCHAR(255), default='account')
    active = db.Column(db.BOOLEAN, default=True)

    @staticmethod
    def deleteOne(proxy_id):
        proxy = ProxyModel.getOne(proxy_id)
        if proxy:
            proxy.delete()

    @staticmethod
    def getOne(proxy_id):
        return ProxyModel.query.filter_by(id=proxy_id).first()

    @staticmethod
    def getMany(session_id, proxy_types: list, proxy_status: dict, union=True):
        current_session: SessionModel = db.session.query(SessionModel).filter_by(id=session_id).first()
        proxies = []

        if current_session:
            proxies = current_session.proxies.filter_by(**proxy_status) if proxy_status else current_session.proxies
            final_proxy_type = 0 if union else 1
            for proxy_type in proxy_types:
                final_proxy_type = (final_proxy_type | proxy_type) if union else (final_proxy_type & proxy_type)
            proxies = proxies.filter(ProxyModel.proxy_for.op('&')(final_proxy_type))
            proxies = proxies.all()

        return list(proxies)

    @staticmethod
    def deleteMany(session_id, proxy_types: list, proxy_status: dict, union=True):
        proxies = ProxyModel.getMany(session_id, proxy_types, proxy_status, union)
        for proxy in proxies:
            ProxyModel.deleteOne(proxy.id)
