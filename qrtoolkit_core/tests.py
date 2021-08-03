from django.core.exceptions import ValidationError
from django.test import TestCase
from qrtoolkit_core.models import QRCode, LinkUrl
from qrtoolkit_core.validators import validate_is_api_mode_qrcode
from string import ascii_letters, digits, punctuation
from random import choice


def generate_text(amount_chars):
    chars_to_pick = ascii_letters + digits + punctuation
    return ''.join([choice(chars_to_pick) for _ in range(amount_chars)])


class QrCodeTestCase(TestCase):
    def setUp(self):
        QRCode.objects.create(title='qr1')

    def test_can_add_basic_info_to_code(self):
        qr = QRCode.objects.get(title__exact='qr1')
        info = generate_text(20)
        qr.basic_info = info
        qr.save()
        qr = QRCode.objects.get(title__exact='qr1')
        self.assertEqual(qr.basic_info, info)

    def test_create_link_url_adds_to_set(self):
        qr = QRCode.objects.get(title__exact='qr1')
        link = LinkUrl.objects.create(url='https://www.stad.gent/', code_id=qr.id, name='stad gent')
        link.save()

        self.assertEqual(qr.urls.count(), 1)
        self.assertEqual(qr.urls.first(), link)

    def test_urls_are_ordered_by_priority(self):
        qr = QRCode.objects.get(title__exact='qr1')
        self.assertEqual(qr.urls.count(), 0)
        link = LinkUrl.objects.create(url='https://stad.gent/1/', code=qr, name='stad gent 1', priority=1.0)
        link2 = LinkUrl.objects.create(url='https://stad.gent/2/', code=qr, name='stad gent 2', priority=2.0)
        link.save()
        link2.save()
        link_set = qr.urls
        self.assertEqual(link_set.count(), 2)
        self.assertEqual(link_set.first(), link2)

    def test_validator_qr_mode_api_call_works_correctly(self):
        qr = QRCode.objects.get(title__exact='qr1')
        qr.mode = QRCode.REDIRECT_MODE_CHOICES.KIOSK
        qr.save()
        link = LinkUrl.objects.create(url='https://stad.gent/1/', code=qr, name='stad gent 1', priority=1.0)
        link.save()
        self.assertRaises(ValidationError, lambda: validate_is_api_mode_qrcode(link.id))

        qr.mode = QRCode.REDIRECT_MODE_CHOICES.API_CALL
        qr.save()
        try:
            validate_is_api_mode_qrcode(link.id)
        except ValidationError:
            self.fail(
                'validate_is_api_mode_qrcode should not throw if a QrCode,'
                ' linked to a specific LinkUrl is in API_CALL mode')
