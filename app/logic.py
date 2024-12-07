from aiogram import types
from app.database import models
from app.database.models import async_session as session


class Player:
    def __init__(self, tg_id):
        self.player_id = tg_id

    def add_answer(self, choice_id):
        choice = session.query(models.Choice).filter_by(id=choice_id).first()

    def get_q_id(self, add=False):
        player_q_id = session.query(models.User)


class Game:
    def check_player_exist(self, tg_id):
        player = session.query(models.User).filter_by(tg_id=tg_id).all()
        if not player:
            return False
        return True

    def create_player(self, tg_id, fullname=None):
        if fullname:
            new_player = models.User(fullname=fullname, tg_id=tg_id)
        else:
            new_player = models.User(tg_id=tg_id)

        session.add(new_player)
        session.commit()
