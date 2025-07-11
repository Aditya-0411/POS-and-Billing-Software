from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from .models import Store,Product, Customer, Invoice, InvoiceItem
from decimal import Decimal


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'description','address']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'store', 'name', 'phone', 'email']
        read_only_fields = ['id', 'store']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



# class InvoiceItemReadSerializer(serializers.ModelSerializer):
#     product = serializers.StringRelatedField()
#
#     class Meta:
#         model = InvoiceItem
#         fields = ['product', 'quantity', 'price']
#
# class InvoiceReadSerializer(serializers.ModelSerializer):
#     customer_name = serializers.CharField(source='customer.name', read_only=True)
#     gst_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
#     gst_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
#     subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
#     total = serializers.DecimalField(max_digits=10, decimal_places=2)
#     items = InvoiceItemReadSerializer(many=True)
#
#     class Meta:
#         model = Invoice
#         fields = [
#             'id', 'customer_name', 'created_at',
#             'subtotal', 'gst_percentage', 'gst_amount', 'total',
#             'items'
#         ]
#
#
# # This serializer is used for writing (POST)
# class InvoiceItemWriteSerializer(serializers.ModelSerializer):
#     product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
#
#     class Meta:
#         model = InvoiceItem
#         fields = ['product', 'quantity']
#
#
#
# class InvoiceSerializer(serializers.ModelSerializer):
#     items = InvoiceItemWriteSerializer(many=True)
#     new_customer = serializers.DictField(write_only=True, required=False)
#     customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)
#
#     class Meta:
#         model = Invoice
#         fields = ['id', 'store', 'customer', 'new_customer', 'created_at', 'total', 'items']
#
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         new_customer_data = validated_data.pop('new_customer', None)
#         store = self.context['request'].user.store
#
#         if new_customer_data:
#             customer = Customer.objects.create(store=store, **new_customer_data)
#         else:
#             customer = validated_data.get('customer')
#             if not customer:
#                 raise serializers.ValidationError({'customer': 'This field is required if new_customer is not provided.'})
#
#         invoice = Invoice.objects.create(store=store, customer=customer)
#
#         total = 0
#         for item_data in items_data:
#             product = item_data['product']
#             quantity = item_data['quantity']
#             price = product.price
#
#             if product.stock < quantity:
#                 raise serializers.ValidationError(f"Insufficient stock for product: {product.name}")
#
#             product.stock -= quantity
#             product.save()
#
#             InvoiceItem.objects.create(invoice=invoice, product=product, quantity=quantity, price=price)
#             total += quantity * price
#
#         invoice.total = total
#         invoice.save()
#         return invoice





class InvoiceItemReadSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'price']


class InvoiceReadSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_address = serializers.CharField(source='store.address', read_only=True)
    store_contact = serializers.CharField(source='store.contact', read_only=True)

    customer_name = serializers.CharField(source='customer.name', read_only=True)
    gst_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    gst_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    items = InvoiceItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'store_name', 'store_address', 'store_contact',
            'customer_name', 'created_at', 'subtotal', 'gst_percentage',
            'gst_amount', 'total', 'items'
        ]

class InvoiceItemWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemWriteSerializer(many=True)
    new_customer = serializers.DictField(write_only=True, required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)

    class Meta:
        model = Invoice
        fields = [
            'id', 'store', 'customer', 'new_customer',
            'created_at', 'gst_percentage', 'subtotal',
            'gst_amount', 'total', 'items'
        ]
        read_only_fields = ['subtotal', 'gst_amount', 'total', 'store', 'created_at']

    def create(self, validated_data):
        request = self.context['request']
        store = request.user.store
        items_data = validated_data.pop('items')
        new_customer_data = validated_data.pop('new_customer', None)

        if new_customer_data:
            customer = Customer.objects.create(store=store, **new_customer_data)
        else:
            customer = validated_data.get('customer')
            if not customer:
                raise serializers.ValidationError({'customer': 'This field is required if new_customer is not provided.'})

        gst_percentage = validated_data.get('gst_percentage', 18)
        invoice = Invoice.objects.create(
            store=store,
            customer=customer,
            gst_percentage=gst_percentage
        )

        subtotal = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price

            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock for {product.name}")

            product.stock -= quantity
            product.save()

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=quantity,
                price=price
            )
            subtotal += price * quantity

        gst_amount = subtotal * (Decimal(gst_percentage) / Decimal('100'))
        total = subtotal + gst_amount

        invoice.subtotal = subtotal
        invoice.gst_amount = gst_amount
        invoice.total = total
        invoice.save()

        return invoice



class InvoiceSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    items = InvoiceItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'store', 'customer_name', 'created_at',
            'gst_percentage', 'gst_amount', 'subtotal', 'total',
            'items'
        ]

class StoreBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'address', 'contact']


class InvoiceDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemReadSerializer(many=True)
    customer_name = serializers.SerializerMethodField()
    store = StoreBasicSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'store', 'customer_name', 'created_at',
            'gst_percentage', 'subtotal', 'gst_amount',
            'total', 'items'
        ]

    def get_customer_name(self, obj):
        return obj.customer.name