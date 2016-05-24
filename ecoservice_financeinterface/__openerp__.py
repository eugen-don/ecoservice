# -*- coding: utf-8 -*-
{
    'name': 'Ecoservice Financial Interface',
    'version': '8.0.1.0.2',
    'depends': [
        'base',
        'account'
    ],
    'author': 'ecoservice',
    'website': 'www.ecoservice.de',
    'description': """The main modul ecoservice_finance provides the basic methods for the finance interface.

Further information under
* Github: https://github.com/ecoservice/ecoservice/ecoservice
* Ecoservice Website https://www.ecoservice.de

""",
    'category': 'Accounting',
    'data': [
        'security/ecofi_security.xml',
        'security/ir.model.access.csv',
        'account_view.xml',
        'account_invoice_view.xml',
        'ecofi_sequence.xml',
        'ecofi_view.xml',
        'res_company_view.xml',
        'wizard/wizard_view.xml'
        ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True
}
