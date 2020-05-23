from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver


@receiver(valid_ipn_received)
def pay_application_fee(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != "sb-azrfj1871887@business.example.com":
            # Not a valid payment
            print(ipn_obj.receiver_email)
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.



        if ipn_obj.mc_gross and ipn_obj.mc_currency == 'USD':
            print(ipn_obj.mc_gross)
            print("got it")
        else:
            print(ipn_obj.mc_gross)
            raise Exception("failed if")

# valid_ipn_received.connect(pay_application_fee)
