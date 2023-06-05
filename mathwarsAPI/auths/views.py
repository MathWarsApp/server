import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from jwt import InvalidTokenError, decode, ExpiredSignatureError
from rest_framework import generics, status
from rest_framework.response import Response
from mathwarsAPI import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from auths.models import RefreshTokenModel, Users
from auths.serializers import UserSerializer


class UserRegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        response = Response({
            'access': str(refresh.access_token),
            'user': {**serializer.data},
        }, status=status.HTTP_201_CREATED)
        response.set_cookie(key='refresh_token', value=str(refresh), httponly=True)

        RefreshTokenModel.objects.create(user=user, refresh_token=str(refresh))

        return response


class UserLoginAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            print('it must working but not')
            return Response(data='Invalid username', status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return JsonResponse({'message': 'Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken.for_user(user)
        except TokenError:
            return JsonResponse({'error': 'Could not generate refresh token'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(user)

        response = Response({
            'access': str(refresh.access_token),
            'user': {**serializer.data},
        }, status=status.HTTP_200_OK)
        response.set_cookie(key='refresh_token', value=str(refresh), httponly=True)
        refresh_token, created = RefreshTokenModel.objects.get_or_create(user=user,
                                                                         defaults={'refresh_token': str(refresh)})
        if not created:
            refresh_token.refresh_token = str(refresh)
            refresh_token.save()

        return response


class UserLogoutAPIView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):

        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return HttpResponseBadRequest('Refresh token not found')

        try:
            refresh_token_obj = RefreshTokenModel.objects.get(refresh_token=refresh_token)
            refresh_token_obj.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest('Invalid refresh token')

        response = JsonResponse({'message': 'User logged out successfully'})
        response.delete_cookie('refresh_token')
        return response


class RefreshTokenAPIView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        print(refresh_token)

        if not refresh_token:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except ExpiredSignatureError:
            return JsonResponse({'error': 'Went wrong'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh_token_obj = RefreshTokenModel.objects.get(refresh_token=refresh_token)
        except ObjectDoesNotExist:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        user = refresh_token_obj.user
        access_token = RefreshToken(refresh_token).access_token
        serializer = self.get_serializer(Users.objects.get(username=user))
        new_refresh_token = RefreshToken.for_user(user)
        refresh_token_obj.refresh_token = str(new_refresh_token)
        refresh_token_obj.save()

        response = Response({
            'access': str(access_token),
            'user': {**serializer.data},
        }, status=status.HTTP_200_OK)
        response.set_cookie(key='refresh_token', value=str(new_refresh_token), httponly=True)

        return response
