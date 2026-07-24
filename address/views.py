from django.shortcuts import get_object_or_404, render

from address.models import Address


def address_list(request):
    addresses = Address.objects.all()
    return render(request, 'address_list.html', {'addresses': addresses})


def address_detail(request, pk):
    address = get_object_or_404(Address, pk=pk)
    return render(request, 'address_detail.html', {'address': address})
