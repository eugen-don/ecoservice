# -*- coding: utf-8 -*-
##############################################################################
#    ecoservice_text_template
#    Copyright (c) 2015 ecoservice GbR (<http://www.ecoservice.de>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This program based on OpenERP.
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
##############################################################################
{
    'name': 'ecoservice: Text Template',
    'version': '1.3.1',
    'author': 'ecoservice',
    'website': 'www.ecoservice.de',
    'category': 'General',
    'depends': [
        'purchase',
        'sale',
    ],
    'data': [
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/account_view.xml',
        'security/ir.model.access.csv'
    ],
    'auto_install': False,
    'application': False,
}
