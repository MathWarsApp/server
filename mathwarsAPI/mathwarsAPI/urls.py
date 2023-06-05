"""
URL configuration for mathwarsAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from auths.views import UserRegistrationAPIView, UserLoginAPIView, UserLogoutAPIView, RefreshTokenAPIView
from game.views import AddPlayerToQueue, GenerateExpression, RemovePlayerFromQueue
from users.views import UsersList, UserDeleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', UserRegistrationAPIView.as_view(), name='register'),
    path('api/login/', UserLoginAPIView.as_view(), name='login'),
    path('api/logout/', UserLogoutAPIView.as_view(), name='login'),
    path('api/refresh/', RefreshTokenAPIView.as_view(), name='login'),
    path('api/users/', UsersList.as_view(), name='users'),
    path('api/to-queue/', AddPlayerToQueue.as_view(), name='to_queue'),
    path('api/remove-queue/', RemovePlayerFromQueue.as_view(), name='remove_queue'),
    path('api/generate-exp/', GenerateExpression.as_view(), name='generate_exp'),
    path('api/user-delete/', UserDeleteView.as_view(), name='user_delete')
]
