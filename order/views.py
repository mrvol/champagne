from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from order.models import Order


def order_list(request):
    orders = Order.objects.all()
    return render(request, 'order_list.html', {'orders': orders})


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {'order': order})


def order_list_api(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)
    return JsonResponse(Order.as_json(Order.objects.all()), safe=False)


def staff_order_list(request):
    return render(request, 'staff_order_list.html')
