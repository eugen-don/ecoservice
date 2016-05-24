# -*- coding: utf-8 -*-

{
    'name': 'Ecoservice Financial Interface Datev Exports',
    'version': '8.0.1.0',
    'depends': [
        'ecoservice_financeinterface'
    ],
    'author': 'ecoservice',
    'website': 'www.ecoservice.de',
    'description': """The module ecoservice_financeinterface_datev_export lets you configure different ascii base data exports.

Details of the module:
* Export of Paymentterms
* Export of Debit and Credit Account

Further information under
* Github: https://github.com/ecoservice/ecoservice/ecoservice
* Ecoservice Website https://www.ecoservice.de
""",
    'category': 'Accounting',
    'data': [
        'datev_export.xml',
        'datev_export_data.xml',
        'wizard/export_ecofi_datev_export.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True
}
