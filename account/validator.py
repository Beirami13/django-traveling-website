from django.core.exceptions import ValidationError
import re


def phone(value):
    """اعتبارسنجی شماره موبایل ایران (مثل 09123456789)"""
    if not re.fullmatch(r'09\d{9}', str(value)):
        raise ValidationError('شماره موبایل معتبر نیست')