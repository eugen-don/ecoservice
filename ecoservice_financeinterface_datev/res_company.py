# -*- coding: utf-8 -*-
""" The res_company module extends the original OpenERP res_company objects with different attributes and methods
"""
##############################################################################
#    ecoservice_financeinterface_datev
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

from openerp import api, fields, models


class ResCompany(models.Model):
    """ Inherits the res.company class and adds methods and attributes

    .. automethod:: _finance_interface_selection
    """
    _inherit = 'res.company'

    @api.multi
    def _finance_interface_selection(self):
        """Appends datev as possible export format

        .. seealso::
            :class:`ecoservice_financeinterface.ecofi.ecofi.ecofi_buchungen`
        """
        res = super(ResCompany, self)._finance_interface_selection()
        res.append(('datev', 'Datev'))
        return res

    finance_interface = fields.Selection(_finance_interface_selection, 'Finance Interface')
    exportmethod = fields.Selection([
        ('netto', 'netto'),
        ('brutto', 'brutto')
    ], 'Exportmethod')
    enable_datev_checks = fields.Boolean('Perform Datev Checks', default=True)
