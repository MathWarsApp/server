from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseBadRequest
from jwt import InvalidTokenError, decode
from rest_framework import generics, status
from rest_framework.response import Response

from auths.models import Users, RefreshTokenModel
from auths.serializers import UserSerializer
from mathwarsAPI import settings
from .serializer import UsersSerializer


class UsersList(generics.ListAPIView):
    serializer_class = UsersSerializer

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
                    # users = Users.objects.all()
                    users = Users.objects.filter(total__gte=10).order_by('-percent', '-total')[:10]
                    serializer = self.serializer_class(users, many=True)
                    return Response(serializer.data)
            except InvalidTokenError:
                return JsonResponse({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except InvalidTokenError:
            return HttpResponseBadRequest('Invalid access token')


class UserDeleteView(generics.DestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return HttpResponseBadRequest('Refresh token not found')

        try:
            refresh_token_obj = RefreshTokenModel.objects.get(refresh_token=refresh_token)
            refresh_token_obj.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('Invalid refresh token')

        try:
            user_id = request.data.get("id")
            if user_id:
                instance = self.get_queryset().get(id=user_id)
                self.perform_destroy(instance)
                response = Response(status=status.HTTP_204_NO_CONTENT)
                response.delete_cookie('refresh_token')
                return response
            else:
                return Response({'error': 'Invalid id'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
