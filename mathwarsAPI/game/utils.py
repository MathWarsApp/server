import uuid


def generate_room_id():
    return uuid.uuid4().hex


def room_init(room, player, player_count):
    player.rooms_id = room.room_id
    player.room_id = room.id
    player.save()
    room.players_count = player_count
    room.save()
