from paypal.standard.forms import PayPalPaymentsForm
from django.utils.html import format_html

class CustomPaypalPaymentsForm(PayPalPaymentsForm):
    def get_html_submit_element(self):
        return format_html(
            """<input type="image" src="{0}" name="submit" alt="compra ahora" /> """,self.get_image()
        )