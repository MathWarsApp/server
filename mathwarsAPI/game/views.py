from django.http import JsonResponse, HttpResponseBadRequest
from jwt import InvalidTokenError, decode
from rest_framework import generics, status
from rest_framework.response import Response
from mathwarsAPI import settings
from .expressions_generetor import ExpressionGenerator
from .models import Rooms, Players
from .serializers import RoomSerializer, PlayerSerializer
from .utils import room_init


class AddPlayerToQueue(generics.CreateAPIView):
    serializer_class = PlayerSerializer

    def post(self, request, *args, **kwargs):
        try:
            auth_header = request.headers['Authorization']
            if not auth_header:
                JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            access_token = request.headers['Authorization'].split(' ')[1]

            if not access_token:
                JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                decoded_token = decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
                if decoded_token:
                    player = Players.objects.create(rooms_id=None, username=request.data['username'])
                    room = Rooms.objects.filter(players_count=1).first()
                    player_serializer = self.get_serializer(player)

                    if room:
                        room_init(room, player, 2)
                        room_serializer = RoomSerializer(room)
                        response_data = {
                            'config_data': room_serializer.data,
                            'user_state': {**player_serializer.data}
                        }
                        return Response(response_data, status=status.HTTP_200_OK)
                    else:
                        room = Rooms.objects.create()
                        room_init(room, player, 1)
                        room_serializer = RoomSerializer(room)
                        response_data = {
                            'config_data': room_serializer.data,
                            'user_state': {**player_serializer.data}

                        }
                        return Response(response_data, status=status.HTTP_201_CREATED)
            except InvalidTokenError:
                return JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except InvalidTokenError:
            return HttpResponseBadRequest('Invalid access token')


class RemovePlayerFromQueue(generics.DestroyAPIView):

    def delete(self, request, *args, **kwargs):
        print(request.data)
        try:
            auth_header = request.headers['Authorization']
            if not auth_header:
                JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            access_token = request.headers['Authorization'].split(' ')[1]

            if not access_token:
                JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                decoded_token = decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
                if decoded_token:
                    try:
                        username = request.data.get('username')
                        player = Players.objects.get(username=username)
                        room = Rooms.objects.get(room_id=player.rooms_id)
                        player.delete()
                        room.delete()
                        return Response(status=status.HTTP_204_NO_CONTENT)

                    except Players.DoesNotExist:
                        return Response({'error': 'Player does not exist.'}, status=status.HTTP_404_NOT_FOUND)
                    except Rooms.DoesNotExist:
                        return Response({'error': 'Room does not exist.'}, status=status.HTTP_404_NOT_FOUND)
                    except Exception as e:
                        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except InvalidTokenError:
                return JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except InvalidTokenError:
            return HttpResponseBadRequest('Invalid access token')


class GenerateExpression(generics.ListAPIView):

    def get(self, request, *args, **kwargs):

        try:
            auth_header = request.headers['Authorization']
            if not auth_header:
                JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            access_token = request.headers['Authorization'].split(' ')[1]

            if not access_token:
                JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            try:
                decoded_token = decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
                if decoded_token:
                    expression = ExpressionGenerator.generate_expression_level_1()
                    return Response({'expression': expression})
            except InvalidTokenError:
                return JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except InvalidTokenError:
            return HttpResponseBadRequest('Invalid access token')
