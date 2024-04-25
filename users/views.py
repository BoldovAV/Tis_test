import uuid

from django.conf import settings
from django.contrib import messages

from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from rest_framework import viewsets


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
            message=f'Ты один из нас, бобро пожаловать. \nПройди по ссылке для активации аккаунта '
                    f'{verify_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[new_user.email]
        )


class VerifyEmailView(View):
    def get(self, request, pk, token):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")

        if user.verification_token == token:
            user.is_active = True
            user.save()
            messages.success(request, 'Ваш аккаунт успешно активирован. Вы можете войти.')
            return redirect('users:user')
        else:
            messages.error(request, 'Неверная ссылка для верификации. Пожалуйста, свяжитесь с администратором.')
            return redirect('users:user')
