from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import braintree

# Create your views here.
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="j63y6647f3rfhdms",
        public_key="qmc5kbkw7g6dwt7v",
        private_key="c9a496cf7af702b1b78f278f32b33116"
    )
)


def validate_user_session(id, token):

    UserModel = get_user_model

    try:
        user = UserModel.objects.get(pk=id)
        if user.session_token == token:
            return True
        return False
    except UserModel.DoesNotExist:
        return False


@csrf_exempt
def generate_token(request, id, token):
    if not validate_user_session(id, token):
        return JsonResponse({'error': 'Invalid session ,Please login again'})

    return JsonResponse({'clintToken': gateway.clint_token.generate(), 'success': True})


@csrf_exempt
def process_payment(request, id, token):
    if not validate_user_session(id, token):
        return JsonResponse({'error': 'Invalid session ,Please login again'})

    nonce_from_the_clint = request.POST["paymentMethodNonce"]
    amount_from_the_clint = request.POST["paymentMethodNonce"]

    result = gateway.transaction.sale({
        "amount": amount_from_the_clint,
        "payment_method_nonce": nonce_from_the_clint,
        "options": {
            "submit_for_settlement": True
        }
    })

    if result.is_sucess:
        return JsonResponse({'success': result.is_success,
                             'transaction': {'id': result.transaction.id,
                                             'amount': result.transaction.amount}
                             })
    else:
        JsonResponse({
            'error': True, 'success': False
        })
