from rest_framework import generics, status
from rest_framework.response import Response
import stripe
from django.conf import settings
from share.permissions import GeneratePermissions
from .serializers import PaymentConfirmSerializer, PaymentStatusSerializer, PaymentCreateSerializer, \
    PaymentSuccessSerializer
from order.models import Order
from share.enums import PaymentProvider

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class PaymentCreateView(GeneratePermissions, generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = PaymentCreateSerializer
    http_method_names = ['patch']
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        else:
            return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'canceled':
            return Response({'detail': 'Order already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        if instance.status == "paid":
            return Response({'detail': 'Order is already paid.'}, status=status.HTTP_400_BAD_REQUEST)

        if instance.status == "shipped":
            return Response({'detail': 'Order has been shipped.'}, status=status.HTTP_400_BAD_REQUEST)

        if instance.status == "delivered":
            return Response({'detail': 'Order has been delivered.'}, status=status.HTTP_400_BAD_REQUEST)

        card_number = request.data.get('card_number')
        expiry_month = request.data.get('expiry_month')
        expiry_year = request.data.get('expiry_year')
        cvc = request.data.get('cvc')

        if not all([card_number, expiry_month, expiry_year, cvc]):
            return Response({'detail': 'Card details are incomplete.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_method = None
        if card_number.startswith('4242') and len(card_number) == 16:
            payment_method = "pm_card_visa"
        elif card_number.startswith('5555') and len(card_number) == 16:
            payment_method = "pm_card_mastercard"

        if instance.payment_method == PaymentProvider.CARD.value:
            intent = stripe.PaymentIntent.create(
                amount=int(instance.amount * 100),
                currency='usd',
                payment_method=payment_method,
                automatic_payment_methods={"enabled": True, 'allow_redirects': 'never'}
            )
            instance.transaction_id = intent['id']
            instance.save()

            intent = stripe.PaymentIntent.retrieve(instance.transaction_id)
            client_secret = intent['client_secret']
            response_data = {
                'client_secret': client_secret
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid payment method.'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentConfirmView(GeneratePermissions, generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = PaymentConfirmSerializer
    http_method_names = ['patch']
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        else:
            return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.status)
        if instance.status != 'pending':
            return Response({'detail': 'Order payment status cannot be updated.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = instance.transaction_id
        try:
            intent = stripe.PaymentIntent.confirm(transaction_id)
            if intent.get('status') != 'succeeded':
                return Response({'status': intent.get('status')}, status=status.HTTP_400_BAD_REQUEST)
            instance.status = 'paid'
            instance.save()

            if hasattr(request.user, 'cart'):
                request.user.cart.items.all().delete()

            return Response({'status': intent.get('status')}, status=status.HTTP_200_OK)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(GeneratePermissions, generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = PaymentStatusSerializer
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        else:
            return None


class PaymentCancelView(GeneratePermissions, generics.UpdateAPIView):
    queryset = Order.objects.all()
    http_method_names = ['patch']
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        else:
            return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == 'canceled':
            return Response({'detail': 'Order already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        if instance.status in ['paid', 'shipped', 'delivered']:
            return Response({'detail': 'Order cannot be canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        instance.status = 'canceled'
        instance.save()

        return Response({'detail': 'Order successfully canceled.'}, status=status.HTTP_200_OK)


class PaymentLinkView(GeneratePermissions, generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = PaymentStatusSerializer
    http_method_names = ['patch']
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        else:
            return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'canceled':
            return Response({'detail': 'Order already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        if instance.status in ['paid', 'shipped', 'delivered']:
            return Response({'detail': 'Order cannot be updated.'}, status=status.HTTP_400_BAD_REQUEST)

        if instance is not None:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order',
                        },
                        'unit_amount': int(instance.amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment/' + str(instance.pk) + '/success/'),
                cancel_url=request.build_absolute_uri('/payment/' + str(instance.pk) + '/cancel/'),
            )

            instance.transaction_id = checkout_session['id']
            instance.save()

            response_data = {
                'url': checkout_session['url']
            }

            return Response(response_data, status=status.HTTP_200_OK)


class PaymentSuccessView(GeneratePermissions, generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = PaymentSuccessSerializer
    http_method_names = ['patch']
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated and obj.user == self.request.user:
            return obj
        return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status in ['paid', 'shipped', 'delivered']:
            return Response({'detail': 'Order cannot be updated.'}, status=status.HTTP_400_BAD_REQUEST)

        if not instance.transaction_id:
            return Response({'detail': 'Transaction ID is missing.'}, status=status.HTTP_400_BAD_REQUEST)

        checkout_session = stripe.checkout.Session.retrieve(instance.transaction_id)

        if checkout_session['payment_status'] == 'paid':
            instance.status = 'paid'
            instance.is_paid = True
            instance.save()

            return Response({'detail': 'Order updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Payment failed.'}, status=status.HTTP_400_BAD_REQUEST)
