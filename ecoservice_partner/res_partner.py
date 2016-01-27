# -*- encoding: utf-8 -*-
""" This module extends the original OpenERP partner object with different attributes and methods
"""
##############################################################################
#    Ecoservice Partner
#    Copyright (c) 2014 ecoservice GbR (<http://www.ecoservice.de>).
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
from openerp import fields, models, api

class res_partner(models.Model):
    """ Inherits the res.partner class and adds methods and attributes
    """
    _inherit = "res.partner"

    name = fields.Char('Name', size=256, select=True)
    first_name = fields.Char('First Name', size=128, required=False, select=True)
    last_name = fields.Char('Last Name', size=128, required=False, select=True)
    get_salutation = fields.Char(compute="_get_salutation_title")
    get_title = fields.Char(compute='_get_salutation_title')

    @api.one
    def _get_salutation_title(self):
        """ Method to get the salutation in the language of the partner
        """
        self.get_salutation = ''
        self.get_title = ''
        if self.title.name:
            lang = self.lang or 'en_US'
            new_partner_data = self.with_context(lang=lang).browse(self.id)
            self.get_salutation = new_partner_data.title.salutation or ''
            self.get_title = new_partner_data.title.name or ''

    @api.onchange('first_name', 'last_name')
    def get_name(self):
        """ OnChange method to write the first_name and last_name into the name

        :param char first_name: The first name of the partner
        :param char last_name: The last name of the partner
        :return: A dictionary with the name
        :rtype: dict
        """
        if self.first_name and self.last_name:
            self.name = self.first_name + ' ' + self.last_name
        elif self.first_name:
            self.name = self.first_name
        elif self.last_name:
            self.name = self.last_name
    
    @api.one
    def write(self, vals):
        """ Inherit write method to insert the first_name and last_name into the name if the partner isn't a company
        """
        first_name = self.first_name
        last_name = self.last_name
        company = self.is_company
        name = self.name
        
        if 'first_name' in vals:
            first_name = vals['first_name']
        if 'last_name' in vals:
            last_name = vals['last_name']
        if 'is_company' in vals:
            company = vals['is_company']
        if 'name' in vals:
            name = vals['name']
        if company:
            vals['name'] = name
            vals['first_name'] = ''
            vals['last_name'] = ''
        else:
            if first_name and last_name:
                vals['name'] = first_name + ' ' + last_name
            elif first_name:
                vals['name'] = first_name
            elif last_name:
                vals['name'] = last_name
        return super(res_partner, self).write(vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """ Inherit create method to insert the first_name and last_name into the name
        """
        first_name = ''
        last_name = ''
        space = ' '
        if not vals.get('is_company', False):
            if 'first_name' in vals and vals['first_name']:
                first_name = vals['first_name']
            if 'last_name' in vals and vals['last_name']:
                last_name = vals['last_name']
            if not first_name or not last_name:
                space = ''
            if last_name or first_name:
                vals['name'] = first_name + space + last_name
        return super(res_partner, self).create(vals)

class res_partner_title(models.Model):
    """ Inherits the res.partner.title class and adds fields
    """
    _inherit = 'res.partner.title'
    
    salutation = fields.Char('Salutation', size=128, translate=True)
    gender  = fields.Selection((('male','male'),('female','female')))
