# -*- encoding: utf-8 -*-
##############################################################################
#    Ecoservice Partner
#    Copyright (c) 2013 ecoservice GbR (<http://www.ecoservice.de>).
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
{   # pylint: disable-msg=W0104
    "name": "Ecoservice Partner", # pylint: disable-msg=W0311
    "version": "1.0",
    "depends": ["base"],
    "author": "ecoservice",
    "website": "www.ecoservice.de",
    "description": """Improvment of partner :
    * Split name in first name and last name for non company partner""",
    "category": "Generic Modules",
    "demo": ['demo/test_demo_data.xml', ],
    "data": ['res_partner_view.xml', ],
    "test": [],
    "css": [],
    "active": False,
    "installable": True,
}