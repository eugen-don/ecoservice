# -*- coding: utf-8 -*-
# pylint: disable-msg=C0111
###############################################################################
#
#    ecoservice_financeinterface_datev
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
#
###############################################################################

from openerp import api, fields, models, _
from . import exceptions


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    enable_datev_checks = fields.Boolean('Perform Datev checks', default=True)

    @api.multi
    def is_datev_validation_active(self):
        self.ensure_one()
        return self.enable_datev_checks and self.env['res.users'].browse(self._uid).company_id.enable_datev_checks

    @api.multi
    def perform_datev_validation(self, throw_exception=False):
        is_validated = True
        error_list = []

        for rec in self:
            if rec.is_datev_validation_active():
                for no, line in enumerate(rec.invoice_line):
                    try:
                        line.perform_datev_validation(throw_exception=throw_exception, line_no=no + 1)
                    except exceptions.DatevWarning as dw:
                        is_validated = False
                        error_list.append(dw.message)

        if throw_exception and not is_applicable:
            raise exceptions.DatevWarning('\n'.join(error_list))

        return is_validated


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def perform_datev_validation(self, throw_exception=False, line_no=None):
        """
        Performs tests on an invoice line for whether the taxes are correctly set or not.

        The major use of this method is in the condition of a workflow transition.

        :param line_no: int Line number to be displayed in an error message.
        :param throw_exception: bool Specifies whether an exception in case of a failed test should be thrown
            or if the checks should be performed silently.
        :return: True if all checks were performed w/o errors or no datev checks are applicable. False otherwise.
        :rtype: bool
        """
        self.ensure_one()
        if not self.perform_datev_validation_applicability_check():
            return True
        is_applicable = len(self.invoice_line_tax_id) == 1 and self.account_id.datev_steuer == self.invoice_line_tax_id
        if throw_exception and not is_applicable:
            raise exceptions.DatevWarning(
                _(u'Line {line_no}: The taxes specified in the invoice line ({tax_line}) and the corresponding account ({tax_account}) mismatch.'.format(
                    line_no=line_no, tax_line=self.invoice_line_tax_id.description, tax_account=self.account_id.datev_steuer.description
                ))
            )
        return is_applicable

    @api.multi
    def perform_datev_validation_applicability_check(self):
        """
        Tests if an invoice line is applicable to datev checks or not.

        :return: True if it is applicable. Otherwise False.
        :rtype: bool
        """
        self.ensure_one()
        return self.account_id.automatic and bool(self.account_id.datev_steuer)
