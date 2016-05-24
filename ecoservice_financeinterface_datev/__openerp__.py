# -*- coding: utf-8 -*-

{
    'name': 'Ecoservice Financial Interface Datev',
    'version': '8.0.1.2.1',
    'depends': [
        'ecoservice_financeinterface',
        'mail'
    ],
    'author': 'ecoservice',
    'website': 'www.ecoservice.de',
    'description': """The module ecoservice_financeinterface_datev provides methods to convert account moves to the Datevformat (Datev Dok.-Nr.: 1036228).

Details of the module:
* Configuration of automatic accounts
* Test of datev accounting rules
 
Further information under
* Github: https://github.com/ecoservice/ecoservice/ecoservice
* Ecoservice Website https://www.ecoservice.de
""",
    'category': 'Accounting',
    'data': [
        'account_view.xml',
        'account_invoice_view.xml',
        'account_cron.xml',
        'res_company_view.xml',
        'ecoservice_financeinterface_datev_installer_view.xml',
        'workflow/account_invoice_workflow.xml'
    ],
    'demo': [],
    'application': False,
    'active': False,
    'installable': True
}
