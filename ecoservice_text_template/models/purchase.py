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


class PurchaseOrderText(models.Model):
    _inherit = 'purchase.order'

    purchase_offer = fields.Html('Purchase Offer Text', translate=True)
    purchase_confirmation = fields.Html('Purchase Confirmation Text', translate=True)


class PurchaseTextTemplate(models.TransientModel):
    _name = 'purchase.text.config.settings'
    _inherit = 'res.config.settings'

    default_purchase_offer = fields.Html('Purchase Offer Text', translate=True, default_model='purchase.order')
    default_purchase_confirmation = fields.Html('Purchase Confirmation Text', translate=True, default_model='purchase.order')