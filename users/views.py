import uuid

from django.conf import settings
from django.contrib import messages

from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from users.models import User
from users.serliazers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        new_user = serializer.save()

        token = uuid.uuid4()
        new_user.verification_token = token

        verify_url = self.request.build_absolute_uri(reverse_lazy(
            'users:verify_email', kwargs={'pk': new_user.pk, 'token': token})
        )
        new_user.set_password(new_user.password)
        new_user.save()

        send_mail(
            subject='Мои поздравления',
            message=f'Ты один из нас, бобро пожаловать. \nПройди по ссылке'
                    f' для активации аккаунта '
                    f'{verify_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[new_user.email]
        )

    def perform_update(self, serializer):
        upd_user = serializer.save()
        password = self.request.data.get('password')
        if password:
            upd_user.set_password(password)
        upd_user.save()


class VerifyEmailAPIView(APIView):
    def get(self, request, pk, token):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")

        if user.verification_token == token:
            user.is_active = True
            user.save()
            messages.success(request, 'Ваш аккаунт успешно активирован.'
                                      ' Вы можете войти.')
        else:
            messages.error(request, 'Неверная ссылка для верификации.'
                                    ' Пожалуйста, свяжитесь с администратором.')


class UserPasswordDropAPIView(APIView):
    """APIView для сброса пароля"""
    def post(self, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)
        new_password = User.objects.make_random_password()
        send_mail(
            subject='Новый пароль',
            message=f'Не теряй больше\n'
                    f'{new_password}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        user.set_password(new_password)
        user.save()
