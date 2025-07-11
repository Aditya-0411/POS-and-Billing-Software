from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import User, Store, Product, Customer, Invoice
from .serializers import (
    StoreSerializer,
    ProductSerializer,
    CustomerSerializer,
    InvoiceCreateSerializer,
    InvoiceReadSerializer, InvoiceDetailSerializer
)


from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Invoice


# 🔐 Helper for generating JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ✅ Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        try:
            password = data.get('password')
            password2 = data.get('password2')

            if password != password2:
                return Response({'error': "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

            validate_password(password)

            user = User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=password
            )
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ✅ Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)
            return Response({
                "message": "Login successful.",
                "tokens": tokens,
                "user": {
                    "username": user.username,
                    "email": user.email
                }
            })
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

# ✅ Create Store View
class StoreCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'store'):
            return Response({"detail": "User already has a store."}, status=400)

        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_store(request):
    try:
        store = request.user.store  # OneToOneField
        serializer = StoreSerializer(store)
        return Response(serializer.data)
    except Store.DoesNotExist:
        return Response({}, status=204)

#modify store
class StoreDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        store = request.user.store
        serializer = StoreSerializer(store)
        return Response(serializer.data)

    def put(self, request):
        store = request.user.store
        serializer = StoreSerializer(store, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

#to view products
class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(store=self.request.user.store)
# ✅ Create Product View
class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['store'] = user.store.id
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Create Customer View
class CustomerCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        store = getattr(user, 'store', None)

        if not store:
            return Response({"detail": "User does not have a store."}, status=400)

        data = request.data.copy()
        serializer = CustomerSerializer(data=data)

        if serializer.is_valid():
            serializer.save(store=store)  # ✅ explicitly assign store
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#TO VIEW CUSTOMERS
class CustomerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        query = request.GET.get('search', '')
        customers = Customer.objects.filter(store=user.store)

        if query:
            customers = customers.filter(name__icontains=query)

        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

class CustomerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk, store=request.user.store)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class CustomerDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk, store=request.user.store)
            customer.delete()
            return Response({"message": "Customer deleted."})
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)

# ✅ Create Invoice View

class CreateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['store'] = request.user.store.id  # optional if serializer gets it from context
        serializer = InvoiceCreateSerializer(data=data, context={'request': request})  # ✅ FIXED HERE
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            print("Invoice creation errors:", serializer.errors)
        return Response(serializer.errors, status=400)

class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invoices = Invoice.objects.filter(store=request.user.store)
        serializer = InvoiceReadSerializer(invoices, many=True)
        return Response(serializer.data)








class InvoicePDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        invoice = Invoice.objects.get(pk=pk, store=request.user.store)
        html_string = render_to_string('invoice_template.html', {'invoice': invoice})
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="invoice_{pk}.pdf"'
        return response

class InvoiceRetrieveView(RetrieveAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceDetailSerializer
    permission_classes = [IsAuthenticated]