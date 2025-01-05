{
    'name': 'advicts Fleet Service Bill',
    'summary': """ Create a Vendors Bill from Fleet Service """,
    'description': """ Create a Vendors Bill from Fleet Service """,
    'author': "GhaithAhmed@Advicts",
    'website': "https://advicts.com",
    'sequence': -10,
    'category': 'Accounting',
    'license': 'LGPL-3',
    'version': '1.0',
    'depends': ['base', 'fleet', 'account_fleet', 'account', 'account_accountant'],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'application': False,
}
