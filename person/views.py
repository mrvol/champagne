from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render

from person.models import User


def login_view(request):
    error = ''
    if request.POST:
        user = authenticate(request, username=request.POST.get('email', '').strip().lower(),
                            password=request.POST.get('password', ''))
        if user:
            auth_login(request, user)
            nxt = request.GET.get('next', '')
            return redirect(nxt if nxt.startswith('/') else 'home')
        error = "That email and password don't match."
    return render(request, 'login.html', {'error': error})


def register(request):
    error = ''
    if request.POST:
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        first, _, last = request.POST.get('name', '').strip().partition(' ')
        if '@' not in email:
            error = 'Enter a valid work email.'
        elif len(password) < 8:
            error = 'The password needs at least 8 characters.'
        elif User.objects.filter(username=email).exists():
            error = 'This email already has an account. Sign in instead.'
        else:
            user = User.objects.create_user(username=email, email=email, password=password,
                                            first_name=first, last_name=last)
            if request.POST.get('role') == 'hiring':
                user.groups.add(Group.objects.get_or_create(name='hiring')[0])
            auth_login(request, user)
            return redirect('home')
    return render(request, 'register.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


def person_list(request):
    people = User.objects.order_by('-id')
    return render(request, 'person_list.html', {'people': people})


def person_detail(request, id):
    person = get_object_or_404(User, id=id)
    return render(request, 'person_detail.html', {'person': person})


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user_detail.html', {'user': user})
