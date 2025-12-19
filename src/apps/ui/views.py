from django.middleware.csrf import get_token
from django.shortcuts import render, redirect

from apps.key.models import Key
from apps.tariff.models import Tariff


def auth(request):
    as_admin = request.GET.get('as_admin') == '1'
    next_url = '/admin/' if as_admin else '/'
    if request.user.is_authenticated:
        return redirect(next_url)
    return render(request, 'auth/page.j2', {'next_url': next_url, "csrftoken": get_token(request)})


def main(request):
    if not request.user.is_authenticated:
        return redirect('/auth/')
    return render(request, 'main/page.j2', {
        'tariffs': Tariff.objects.order_by('price').all(),
    })


def key(request, pk):
    key = Key.objects.filter(pk=pk, user=request.user).first()
    if not key:
        return redirect('/')
    return render(request, 'key/page.j2', {
        'tariffs': Tariff.objects.order_by('price').all(),
        'key': key,
    })


def balance(request):
    return render(request, 'balance/page.j2', {})
