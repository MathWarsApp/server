import json
import math

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import random

from auths.models import Users
from game.models import Rooms, Players
from game.serializers import PlayerSerializer


def check_answer(expression, answer):
    result = math.floor(eval(expression))
    return result == int(answer)


def attack_player(enemy_remain_hp, enemy_has_armor=False):
    # operators = ['+', '-']
    # x = random.randint(1, 25)
    # operator = random.choice(operators)
    damage = random.randint(15, 25)
    print(damage)
    if enemy_has_armor:
        result = enemy_remain_hp - (damage - (damage * 0.25))
        print(result)
    else:
        result = enemy_remain_hp - damage
        print(result)

    return math.floor(result)


class RoomConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, **kwargs):
        player_count = Rooms.objects.filter(players_count=2, room_id=self.room_name)

        if player_count:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "room_message", "start_game": 'start'}
            )
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "room_message", "start_game": 'wait'}
            )

    def room_message(self, event):
        message = event["start_game"]
        self.send(text_data=json.dumps({"start_game": message}))


class MatchConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "game_%s" % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, **kwargs):
        game_status = json.loads(kwargs['text_data'])
        users_data = {}

        if game_status["game_status"] == "starting":
            users_data = Players.objects.filter(rooms_id=self.room_name)
            serializer = PlayerSerializer(users_data, many=True)
            if users_data[0].state != 'sleep' and users_data[0].state != 'active':
                second_player = users_data[1]
                second_player.state = "sleep"
                second_player.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {"type": "game_starting",
                 "game_info": {'user_1': {**serializer.data[0]}, 'user_2': {**serializer.data[1]}}}
            )

        elif game_status["game_status"] == "started":
            result = check_answer(game_status["expression"], game_status["userAnswer"])
            enemy_remain_hp = attack_player(game_status["enemy"]["remain_hp"], game_status["enemy"]["has_armor"])

            if enemy_remain_hp <= 0:
                users_data["win"] = game_status["current"]["username"]
                Rooms.objects.filter(room_id=self.scope["url_route"]["kwargs"]["room_id"]).delete()
                current = Users.objects.get(username=game_status["current"]["username"])
                current.total += 1
                current.win += 1
                current.save()
                current = Users.objects.get(username=game_status["current"]["username"])
                current.percent = math.floor(current.win / (current.total / 100))
                current.save()
                enemy = Users.objects.get(username=game_status["enemy"]["username"])
                enemy.total += 1
                enemy.lose += 1
                enemy.save()
                enemy = Users.objects.get(username=game_status["enemy"]["username"])
                enemy.percent = math.floor(enemy.win / (enemy.total / 100))
                enemy.save()

                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "game_started", "game_info": users_data}
                )
                return
            if result:
                if game_status["current"]["action"] == 'attack':
                    current = Players.objects.get(username=game_status["current"]["username"])
                    enemy = Players.objects.get(username=game_status["enemy"]["username"])
                    current.action = None
                    current.state = 'wait'
                    enemy.state = 'sleep'
                    enemy.remain_hp = enemy_remain_hp
                    enemy.has_armor = False
                    current.save()
                    enemy.save()
                    serializer_current = PlayerSerializer(current)
                    serializer_enemy = PlayerSerializer(enemy)
                    users_data = {"user_1": serializer_current.data, "user_2": serializer_enemy.data}
                elif game_status["current"]["action"] == 'defense':
                    current = Players.objects.get(username=game_status["current"]["username"])
                    enemy = Players.objects.get(username=game_status["enemy"]["username"])
                    current.action = None
                    current.state = 'wait'
                    current.has_armor = True
                    enemy.state = 'sleep'
                    current.save()
                    enemy.save()
                    serializer_current = PlayerSerializer(current)
                    serializer_enemy = PlayerSerializer(enemy)
                    users_data = {"user_1": serializer_current.data, "user_2": serializer_enemy.data}
            else:
                current = Players.objects.get(username=game_status["current"]["username"])
                enemy = Players.objects.get(username=game_status["enemy"]["username"])
                current.state = 'wait'
                enemy.state = 'sleep'
                current.save()
                enemy.save()
                serializer_current = PlayerSerializer(current)
                serializer_enemy = PlayerSerializer(enemy)
                users_data = {"user_1": serializer_current.data, "user_2": serializer_enemy.data}
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "game_started", "game_info": users_data}
            )
        elif game_status["game_status"] == "surrender":
            users_data["win"] = game_status["enemy"]["username"]
            Rooms.objects.filter(room_id=self.scope["url_route"]["kwargs"]["room_id"]).delete()
            current = Users.objects.get(username=game_status["current"]["username"])
            current.total += 1
            current.lose += 1
            current.save()
            current = Users.objects.get(username=game_status["current"]["username"])
            current.percent = math.floor(current.win / (current.total / 100))
            current.save()
            enemy = Users.objects.get(username=game_status["enemy"]["username"])
            enemy.total += 1
            enemy.win += 1
            enemy.save()
            enemy = Users.objects.get(username=game_status["enemy"]["username"])
            enemy.percent = math.floor(enemy.win / (enemy.total / 100))
            enemy.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "game_started", "game_info": users_data}
            )
            return

    def game_starting(self, event):
        message = event["game_info"]
        self.send(text_data=json.dumps({"game_info": message}))

    def game_started(self, event):
        message = event["game_info"]
        self.send(text_data=json.dumps({"game_info": message}))
