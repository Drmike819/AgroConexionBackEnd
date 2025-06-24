from django.urls import path
from .views import InvoicesView, InvoiceListView, InvoiceDetailView, InvoiceFromCartView

urlpatterns = [
    path('create/', InvoicesView.as_view(), name='create-invoice'),
    path('list-invoice/', InvoiceListView.as_view(), name='list-invoices'),
    path('invoice/<int:id>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoice/from-cart/', InvoiceFromCartView.as_view(), name='invoice-from-cart')

]
