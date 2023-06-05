from django.db import models

from game.utils import generate_room_id


class RoomManager(models.Manager):
    def get_with_player_count(self):
        return self.annotate(player_count=models.Count('player'))


class PlayerManager(models.Manager):
    def get_players_in_room(self, room):
        return self.filter(room=room)


class Rooms(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.CharField(default=generate_room_id(), null=True)
    players_count = models.IntegerField(default=0, null=True)
    objects = RoomManager()


class Players(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, null=True)
    rooms_id = models.CharField(null=True, default=None)
    username = models.CharField(max_length=255, unique=True)
    total_hp = models.IntegerField(default=100)
    remain_hp = models.IntegerField(default=100)
    action = models.CharField(default=None, null=True)
    has_armor = models.BooleanField(default=False)
    state = models.CharField(default='wait')
    objects = PlayerManager()
