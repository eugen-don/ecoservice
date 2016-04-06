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

from openerp import models, fields


class SaleOrderText(models.Model):
    _inherit = 'sale.order'

    sale_offer = fields.Html('Sale Offer Text', translate=True)
    sale_confirmation = fields.Html('Sale Confirmation Text', translate=True)
    sale_receipt = fields.Html('Sale Receipt Text', translate=True)

class SaleTextTemplate(models.TransientModel):
    _name = 'sale.text.config.settings'
    _inherit = 'res.config.settings'

    default_sale_offer = fields.Html('Sale Offer Text', translate=True, default_model='sale.order')
    default_sale_confirmation = fields.Html('Sale Confirmation Text', translate=True, default_model='sale.order')
    default_sale_receipt = fields.Html('Sale Receipt Text', translate=True, default_model='sale.order')