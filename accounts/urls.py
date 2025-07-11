from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    StoreCreateView,
    ProductCreateView,
    ProductListView,
    CustomerCreateView,
    CustomerListView,
    CustomerDeleteView,
    CustomerUpdateView,
    CreateInvoiceView,
    InvoiceListView, StoreDetailView, InvoiceRetrieveView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('store/create/', StoreCreateView.as_view(), name='create_store'),
    path('store/', StoreDetailView.as_view(), name='store-detail'),


    path('product/create/', ProductCreateView.as_view(), name='add_product'),
    path('products/', ProductListView.as_view(), name='product-list'),

    path('customers/create/', CustomerCreateView.as_view(), name='add_customer'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
path('customers/<int:pk>/update/', CustomerUpdateView.as_view(), name='customer-update'),


    path('invoice/create/', CreateInvoiceView.as_view(), name='invoice-create'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
path('invoices/<int:pk>/', InvoiceRetrieveView.as_view(), name='invoice-detail'),
]
