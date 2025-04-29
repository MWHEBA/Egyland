"""
متغيرات السياق المستخدمة في جميع القوالب
"""
from django.conf import settings

def company_info(request):
    """
    يضيف متغيرات تحتوي معلومات الشركة لاستخدامها في جميع القوالب
    """
    return {
        'company_name': 'Egyland',
        'company_full_name': 'Egyland Agricultural Export',
        'company_description': 'Premium Egyptian Agricultural Export Company.',
        'company_address': 'Cairo, Egypt',
        'company_phone': '+20 123 456 7890',
        'company_email': 'info@egyland.com',
        'company_facebook': 'https://facebook.com/egyland',
        'company_instagram': 'https://instagram.com/egyland',
        'company_linkedin': 'https://linkedin.com/company/egyland',
        'company_twitter': 'https://twitter.com/egyland',
        'copyright_year': '2025',
        'under_construction': getattr(settings, 'UNDER_CONSTRUCTION', True),
    } 