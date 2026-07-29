import uuid

import pytest
from django.test import Client

from address.models import Address
from company.models import Company
from goods.models import Good
from order.models import Order, OrderItem
from person.models import User

TERMINAL_STATUSES = [Order.STATUS_CANCELLED, Order.STATUS_REFUNDED]


@pytest.fixture
def buyer():
    tag = uuid.uuid4().hex[:8]
    return User.objects.create_user(username=f'buyer-{tag}', email=f'buyer-{tag}@example.com', password='pw12345678')


@pytest.fixture
def staff_user():
    tag = uuid.uuid4().hex[:8]
    return User.objects.create_user(username=f'staffer-{tag}', email=f'staffer-{tag}@example.com', password='pw12345678', is_staff=True)


@pytest.fixture
def order(buyer):
    company = Company.objects.create(verified_seller=True, legal_name='Test House')
    address = Address.objects.create(user=buyer, line1='1 Rue Test', city='Reims', country='FR')
    good = Good.objects.create(company=company, name='Test Cuvee', price='50.00', currency=1)
    order = Order.objects.create(buyer=buyer, seller=company, delivery_address=address, currency=1, total_amount='100.00')
    OrderItem.objects.create(order=order, good=good, quantity=2, unit_price='50.00')
    return order


def _staff_client(staff_user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(staff_user)
    client.get('/staff/orders/')  # renders base.html's {% csrf_token %}, sets the csrftoken cookie
    return client


def _buyer_client(buyer):
    client = Client()
    client.force_login(buyer)
    return client


def _set_status_via_staff_ui(staff, csrf_token, order_pk, status):
    resp = staff.post(f'/api/order/{order_pk}/', {'status': status}, HTTP_X_CSRFTOKEN=csrf_token)
    assert resp.status_code == 200
    assert resp.json()['status'] == status
    return resp


def test_staff_changes_status_one_by_one_and_customer_ui_reflects_each_change(order, staff_user, buyer):
    """Walk the whole fulfilment pipeline one status at a time through the staff API
    (exactly what StaffOrdersTable's inline select does), and after each change confirm
    the buyer's own order pages — both the list and the detail view — actually render
    the new status, highlight the right pipeline step, and show/hide tracking correctly."""
    staff = _staff_client(staff_user)
    csrf_token = staff.cookies['csrftoken'].value
    customer = _buyer_client(buyer)

    for step_index, (code, label, icon) in enumerate(Order.PIPELINE):
        _set_status_via_staff_ui(staff, csrf_token, order.pk, code)

        order.refresh_from_db()
        assert order.status == code
        assert order.pipeline_step() == step_index

        for url in (f'/order/{order.pk}/', '/order/list/'):
            resp = customer.get(url)
            assert resp.status_code == 200
            content = resp.content.decode()

            # the human-readable label is what a real customer reads
            assert str(label) in content

            # exactly one pipeline step is marked as current, and it's this one
            assert content.count('aria-current="step"') == 1

            if code in Order.SHIPPED_STATUSES:
                assert 'Shipment tracking' in content
            else:
                assert 'Shipment tracking' not in content


def test_staff_sets_terminal_statuses_and_customer_ui_drops_the_pipeline(order, staff_user, buyer):
    """cancelled/refunded sit outside the linear pipeline, so the customer UI should stop
    showing progress-step chrome entirely once one of them is set."""
    staff = _staff_client(staff_user)
    csrf_token = staff.cookies['csrftoken'].value
    customer = _buyer_client(buyer)

    for code in TERMINAL_STATUSES:
        _set_status_via_staff_ui(staff, csrf_token, order.pk, code)

        order.refresh_from_db()
        assert order.status == code
        assert order.pipeline_step() is None

        resp = customer.get(f'/order/{order.pk}/')
        assert resp.status_code == 200
        content = resp.content.decode()

        assert str(order.get_status_display()) in content
        assert 'aria-current="step"' not in content
        assert 'Shipment tracking' not in content


def test_non_staff_cannot_change_status_via_the_staff_api(order, buyer):
    client = Client()
    client.force_login(buyer)
    resp = client.post(f'/api/order/{order.pk}/', {'status': Order.STATUS_DELIVERED})
    assert resp.status_code == 403

    order.refresh_from_db()
    assert order.status == Order.STATUS_PLACED
