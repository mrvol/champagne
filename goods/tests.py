import uuid

import pytest
from django.test import Client

from company.models import Company
from goods.models import Good
from person.models import User


@pytest.fixture
def good():
    company = Company.objects.create(verified_seller=True)
    return Good.objects.create(company=company, name='Test Good', price='10.00', currency=1)


@pytest.fixture
def staff_user():
    tag = uuid.uuid4().hex[:8]
    return User.objects.create_user(username=f'staffer-{tag}', email=f'staffer-{tag}@example.com', password='pw12345678', is_staff=True)


def test_good_detail_api_get(good, staff_user):
    client = Client()
    client.force_login(staff_user)
    resp = client.get(f'/api/good/{good.pk}/')
    assert resp.status_code == 200
    assert resp.json()['name'] == 'Test Good'


def test_good_detail_api_get_requires_staff(good):
    resp = Client().get(f'/api/good/{good.pk}/')
    assert resp.status_code == 403


def test_good_detail_api_post_without_csrf_token_is_forbidden(good, staff_user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff_user)
    resp = client.post(f'/api/good/{good.pk}/', {'name': 'Renamed', 'price': '10.00'})
    assert resp.status_code == 403


def test_good_detail_api_post_with_csrf_token_saves(good, staff_user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff_user)
    client.get(f'/good/{good.pk}/')  # renders base.html's {% csrf_token %}, sets the csrftoken cookie
    csrf_token = client.cookies['csrftoken'].value

    resp = client.post(
        f'/api/good/{good.pk}/',
        {'name': 'Renamed', 'price': '20.00'},
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert resp.status_code == 200
    assert resp.json()['name'] == 'Renamed'

    good.refresh_from_db()
    assert good.name == 'Renamed'
    assert str(good.price) == '20.00'
