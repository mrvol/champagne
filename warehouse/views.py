from django.shortcuts import get_object_or_404, render

from warehouse.models import Stock, Warehouse


def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'warehouse_list.html', {'warehouses': warehouses})


def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    return render(request, 'warehouse_detail.html', {'warehouse': warehouse})


def stock_list(request):
    stock = Stock.objects.all()
    return render(request, 'stock_list.html', {'stock': stock})


def stock_detail(request, pk):
    item = get_object_or_404(Stock, pk=pk)
    return render(request, 'stock_detail.html', {'item': item})
