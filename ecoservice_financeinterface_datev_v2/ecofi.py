# -*- encoding: utf-8 -*-
""" The ecofi module extends the original OpenERP ecofi objects with different attributes and methods
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
from osv import osv
from decimal import Decimal
from tools.translate import _
from tools import ustr
from copy import deepcopy
import netsvc
logger = netsvc.Logger()


class ecofi(osv.osv):
    """Inherits the ecofi class and adds methods and attributes
    """
    _inherit = 'ecofi'

    def field_config(self, cr, uid, move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict):
        """ Method that generates gets the values for the different Datev columns.
        :param cr: the current row, from the database cursor
        :param uid: the current user’s ID for security checks
        :param move: account_move
        :param line: account_move_line
        :param errorcount: Errorcount
        :param partnererror: Partnererror
        :param thislog: Log
        :param thismovename: Movename
        :param faelligkeit: Fälligkeit
        """
        thisdate = move.date
        datevdict['Datum'] = '%s%s' % (thisdate[8:10], thisdate[5:7])
        if move.name:
            datevdict['Beleg1'] = ustr(move.name)
        if move.journal_id.type == 'purchase' and move.ref:
            datevdict['Beleg1'] = ustr(move.ref)
        datevdict['Beleg1'] = datevdict['Beleg1'][-12:]
        if faelligkeit:
            datevdict['Beleg2'] = faelligkeit
        datevdict['Waehrung'], datevdict['Kurs'] = self.format_waehrung(cr, uid, line, context={'lang': 'de_DE', 'date': thisdate})
        if line.move_id.ecofi_buchungstext:
            datevdict['Buchungstext'] = ustr(line.move_id.ecofi_buchungstext)
        if line.account_id.ustuebergabe:
            if move.partner_id:
                if move.partner_id.vat:
                    datevdict['EulandUSTID'] = ustr(move.partner_id.vat)
            if datevdict['EulandUSTID'] == '':
                errorcount += 1
                partnererror.append(move.partner_id.id)
                thislog += thismovename + _("Error: No sales tax identification number stored in the partner!\n")
        return (errorcount, partnererror, thislog, thismovename, datevdict)

    def pre_export(self, cr, uid, account_move_ids, context={}):
        for move in self.pool.get('account.move').browse(cr, uid, account_move_ids):
            for line in move.line_id:
                if line.account_id.automatic is True and line.account_id.datev_steuer:
                    if line.ecofi_taxid.id != line.account_id.datev_steuer.id:
                        self.pool.get('account.move.line').write(cr, uid, [line.id], {'ecofi_taxid': line.account_id.datev_steuer.id}, context=context, check=False, update_check=False)
                else:
                    if line.ecofi_taxid:
                        self.pool.get('account.move.line').write(cr, uid, [line.id], {'ecofi_taxid': False}, context=context, check=False, update_check=False)
        return super(ecofi, self).pre_export(cr, uid, account_move_ids, context=context)
        
    def datev_brutto(self, cr, uid, move, datev_lines, context=None):
        """ Method that generates calculates the Datev-Brutto Method
        """
        if context is None:
            context = {}
        automatic_diff = {}
        counterpart_lines = {}
        ##Aufsplitten des Moves in Moves pro Gegenkonto
        for datev_line in datev_lines:
            line = datev_line['line']
            if line.ecofi_account_counterpart.code not in counterpart_lines:
                counterpart_lines[line.ecofi_account_counterpart.code] = []
            counterpart_lines[line.ecofi_account_counterpart.code].append(datev_line)
        for counterpart_move in counterpart_lines:
            for datev_line in counterpart_lines[counterpart_move]:
                line = datev_line['line']
                lineumsatz = Decimal(str(0))
                lineumsatz += Decimal(str(line.debit))
                lineumsatz -= Decimal(str(line.credit))
                if line.amount_currency != 0:
                    lineumsatz = Decimal(str(line.amount_currency))
                    context['waehrung'] = True
                ##Automatikkontenberechnung 
                if line.account_id.automatic and not line.ecofi_bu == '40':     
                    context['return_calc'] = True
                    tax_debit = 0.0
                    tax_credit = 0.0
                    taxcalc_ids = self.pool.get('ecofi').calculate_tax(cr, uid, line, context)
                    for taxcalc_id in taxcalc_ids:
                        taxaccount = taxcalc_id['account_paid_id'] and taxcalc_id['account_paid_id'] or taxcalc_id['account_collected_id']
                        if taxaccount:
                            datev_account_code = self.pool.get('account.account').read(cr, uid, taxaccount, context=context)['code']
                            dictcode = '%s_%s' % (datev_account_code, line.id) 
                            tax_debit += taxcalc_id['amount']>0 and taxcalc_id['amount']
                            tax_credit += taxcalc_id['amount']<0 and -taxcalc_id['amount']
                            if dictcode not in automatic_diff:
                                automatic_diff[dictcode] = {'tax_debit': 0.0,
                                                            'tax_credit': 0.0,
                                                            'datevdict': {},
                                                            'datev_code': datev_account_code,
                                                            'datev_account': taxaccount,
                                                        }
                            automatic_diff[dictcode]['tax_debit'] += tax_debit
                            automatic_diff[dictcode]['tax_credit'] += tax_credit
                            automatic_diff[dictcode]['datevdict'] = datev_line['datevdict']         
                    linetax = Decimal(str(0))
                    linetax += Decimal(str(tax_debit))
                    linetax -= Decimal(str(tax_credit))
                    umsatz, sollhaben = self.format_umsatz(cr, uid, lineumsatz + linetax, context=context)
                    datev_line['datevdict']['Sollhaben'] = sollhaben
                    datev_line['datevdict']['Umsatz'] = umsatz
                    datev_line['datevdict']['AutomatikKonto'] = True
            ##Steuerkorrektur z.B. durch Automatikkonto wird der Steuerbetrag bereits innerhalb des Bruttowerts übergeben von daher wird die Steuerzeile um den Steuerbetrag reduziert.
            for konto in automatic_diff:
                for datev_line in counterpart_lines[counterpart_move]:
                    line = datev_line['line']
                    if line.account_id.code == automatic_diff[konto]['datev_code']:
                        lineumsatz = self.format_umsatz_reverse(cr, uid, datev_line['datevdict']['Umsatz'], datev_line['datevdict']['Sollhaben'], context)                 
                        linediff = Decimal(str(0))
                        linediff -= Decimal(str(automatic_diff[konto]['tax_debit']))
                        linediff += Decimal(str(automatic_diff[konto]['tax_credit']))
                        umsatz, sollhaben = self.format_umsatz(cr, uid, lineumsatz + linediff, context=context)
                        datev_line['datevdict']['Sollhaben'] = sollhaben
                        datev_line['datevdict']['Umsatz'] = umsatz
                        automatic_diff[konto]['tax_debit'] = 0.00
                        automatic_diff[konto]['tax_credit'] = 0.00
                        datev_line['datevdict']['AutomatikKonto'] = True
            #Anlegen von Neuen Zeilen die sich anhand einer Steuerdifferenz ergeben, z.B. im ERP 7% Steuer gebucht Datevkonto allerdings 19% dann wird nun die Zeile mit den 19% hinzugefügt
            for konto in automatic_diff:
                if automatic_diff[konto]['tax_debit'] != 0.00 or automatic_diff[konto]['tax_credit'] != 0.00:
                    lineumsatz = Decimal(str(0))
                    lineumsatz -= Decimal(str(automatic_diff[konto]['tax_debit']))
                    lineumsatz += Decimal(str(automatic_diff[konto]['tax_credit']))
                    umsatz, sollhaben = self.format_umsatz(cr, uid, lineumsatz, context=context)
                    datevdict = deepcopy(automatic_diff[konto]['datevdict']) 
                    datevdict['Umsatz'] = umsatz
                    datevdict['Sollhaben'] = sollhaben
                    datevdict['Gegenkonto'] = automatic_diff[konto]['datev_code']
                    datevdict['AutomatikKonto'] = True
                    counterpart_lines[counterpart_move].append({'line': False, 'datev_account': automatic_diff[konto]['datev_account'], 'datevdict': datevdict})
        final_lines = []
        for counterpart_move in counterpart_lines:
            for datev_line in counterpart_lines[counterpart_move]:
                final_lines.append(datev_line)    
        return final_lines

    def datev_ust_correction(self, cr, uid, datev_lines, context=None):
        if context is None:
            context = {}
        newlines = []
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for datev_line in datev_lines:
            if not 'AutomatikKonto' in datev_line['datevdict']:
                continue
            this_account_id = False
            tax_config = []
            if datev_line['line']:
                this_account_id = datev_line['line'].account_id.id
                tax_config = self.get_tax(cr, this_account_id)
            else:
                if 'datev_account' in datev_line:
                    this_account_id = datev_line['datev_account']
                    tax_config = self.get_tax(cr, this_account_id)
            if len(tax_config) == 1:
                tax_object = self.pool.get('account.tax').browse(cr, uid, tax_config[0], context=context)
                lineumsatz = self.format_umsatz_reverse(cr, uid, datev_line['datevdict']['Umsatz'], datev_line['datevdict']['Sollhaben'], context)
                if lineumsatz != Decimal(str(0)):
                    tax = self.calc_tax(cr, uid, tax_object, float(lineumsatz), context=context)
                    if tax != 0.0:
                        nettoamount = Decimal(str(round((lineumsatz / Decimal(str(tax))) * lineumsatz, precision))) 
                        bruttoamount = nettoamount + lineumsatz
                        umsatz_brutto, sollhaben_brutto = self.format_umsatz(cr, uid, Decimal(str(bruttoamount)), context=context)
                        umsatz_netto, sollhaben_netto = self.format_umsatz(cr, uid, Decimal(str(nettoamount * -1)), context=context)
                        datev_line['datevdict']['Umsatz'] = umsatz_brutto
                        datev_line['datevdict']['Sollhaben'] = sollhaben_brutto
                        datev_line['datevdict']['Gegenkonto'] = tax_object.datev_default_account and tax_object.datev_default_account.code or "False"
                        datev_line['datevdict']['Buschluessel'] = str(tax_object.buchungsschluessel)
                        datevdict = deepcopy(datev_line['datevdict']) 
                        datevdict['Umsatz'] = umsatz_netto
                        datevdict['Sollhaben'] = sollhaben_netto
                        datevdict['Gegenkonto'] = tax_object.datev_default_account and tax_object.datev_default_account.code or "False"
                        datevdict['Buschluessel'] = ''
                        newlines.append({'line': False, 'datevdict': datevdict})
        for newline in newlines:
            datev_lines.append(newline)
        return datev_lines
    
    def format_umsatz_reverse(self, cr, uid, lineumsatz, Sollhaben, context={}):
        """ Reverts the formatted amount
        :param cr: the current row, from the database cursor
        :param uid: the current user’s ID for security checks
        :param lineumsatz: amountC
        :param context: context arguments, like lang, time zone
        :param lineumsatz:
        :param context:
        """
        Umsatz = Decimal(lineumsatz.replace(',', '.'))
        if Sollhaben == 's':
            Umsatz = Umsatz * -1
        return Umsatz
    
    def format_umsatz(self, cr, uid, lineumsatz, context={}):
        """ Returns the formatted amount
        :param cr: the current row, from the database cursor
        :param uid: the current user’s ID for security checks
        :param lineumsatz: amountC
        :param context: context arguments, like lang, time zone
        :param lineumsatz:
        :param context:
        """
        Umsatz = ''
        Sollhaben = ''
        if lineumsatz < 0:
            Umsatz = str(lineumsatz * -1).replace('.', ',')
            Sollhaben = 's'
        if lineumsatz > 0:
            Umsatz = str(lineumsatz).replace('.', ',')
            Sollhaben = 'h'
        if lineumsatz == 0:
            Umsatz = str(lineumsatz).replace('.', ',')
            Sollhaben = 's'
        return Umsatz, Sollhaben

    def format_waehrung(self, cr, uid, line, context={}):
        """ Formats the currency for the export
        :param cr: the current row, from the database cursor
        :param uid: the current user’s ID for security checks
        :param line: account_move_line
        :param context: context arguments, like lang, time zone
        """
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        Waehrung = False
        if user.company_id:
            Waehrung = user.company_id.currency_id.id
        else:
            thiscompany = self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
            thiscompany = self.pool.get('res.company').browse(cr, uid, [thiscompany], context=context)[0]
            Waehrung = thiscompany.currency_id.id
        if line.currency_id:
            Waehrung = line.currency_id.id
        if Waehrung:
            thisw = self.pool.get('res.currency').browse(cr, uid, Waehrung, context=context)
            Waehrung = thisw.name
            if Waehrung != 'EUR':
                Faktor = ustr(thisw.rate).replace('.', ',')
            else:
                Faktor = ''
        return Waehrung, Faktor

    def generate_csv(self, cr, uid, ecofi_csv, bookingdict, log, context={}):
        """ Implements the generate_csv method for taxamountthe datev interface
        """
        if context.has_key('export_interface'):
            if context['export_interface'] == 'datev':
                ecofi_csv.writerow(bookingdict['buchungsheader'])
                for buchungsatz in bookingdict['buchungen']:
                    ecofi_csv.writerow(buchungsatz)
        (ecofi_csv, log) = super(ecofi, self).generate_csv(cr, uid, ecofi_csv, bookingdict, log, context=context)
        return ecofi_csv, log    
        
    def generate_csv_move_lines(self, cr, uid, move, buchungserror, errorcount, thislog, thismovename, exportmethod,
                          partnererror, buchungszeilencount, bookingdict, context={}):
        """ Implements the generate_csv_move_lines method for the datev interface     
        """
        if context.has_key('export_interface'):
            if context['export_interface'] == 'datev':
                if bookingdict.has_key('buchungen') is False:
                    bookingdict['buchungen'] = []
                if bookingdict.has_key('buchungsheader') is False:
                    bookingdict['buchungsheader'] = self.buchungenHeaderDatev()    
                faelligkeit = False
                datev_lines = []
                for line in move.line_id:
                    datevkonto = line.ecofi_account_counterpart.code
                    datevgegenkonto = ustr(line.account_id.code)
                    if datevgegenkonto == datevkonto:
                        if line.date_maturity:
                            faelligkeit = '%s%s%s' % (line.date[8:10], line.date[5:7], line.date[2:4])
                        continue
                    lineumsatz = Decimal(str(0))
                    lineumsatz += Decimal(str(line.debit))
                    lineumsatz -= Decimal(str(line.credit))
                    if line.amount_currency != 0:
                        lineumsatz = Decimal(str(line.amount_currency))
                    buschluessel = line.ecofi_bu or ''
                    umsatz, sollhaben = self.format_umsatz(cr, uid, lineumsatz, context=context)           
                    datevdict = {'Sollhaben': sollhaben, 
                                 'Umsatz': umsatz, 
                                 'Gegenkonto': datevgegenkonto, 
                                 'Datum':'',
                                 'Konto': datevkonto, 
                                 'Beleg1':'', 
                                 'Beleg2':'',
                                 'Waehrung':'', 
                                 'Buschluessel': buschluessel,
                                 'Kost1':'',
                                 'Kost2':'', 
                                 'Kostmenge':'', 
                                 'Skonto':'', 
                                 'Buchungstext':'',
                                 'EulandUSTID':'', 
                                 'EUSteuer':'', 
                                 'Basiswaehrungsbetrag':'',
                                 'Basiswaehrungskennung':'', 
                                 'Kurs':'', 
                                 'Movename': ustr(move.name)
                                 }
                    (errorcount, partnererror, thislog, thismovename, datevdict) = self.field_config(cr,
                                                                    uid, move, line, errorcount, partnererror, thislog, 
                                                                    thismovename, faelligkeit, datevdict)
                    datev_lines.append({'datevdict': datevdict,
                                        'line': line,
                                        })
                if exportmethod == 'brutto':
                    datev_lines = self.datev_brutto(cr, uid, move, datev_lines)
                    datev_lines = self.datev_ust_correction(cr, uid, datev_lines)       
                for datev_line in datev_lines:
                    bookingdict['buchungen'].append(self.buchungenCreateDatev(datev_line['datevdict']))
                    buchungszeilencount += 1
        buchungserror, errorcount, thislog, partnererror, buchungszeilencount, bookingdict = super(ecofi, self).generate_csv_move_lines(cr,
            uid, move, buchungserror, errorcount, thislog, thismovename, exportmethod, partnererror, buchungszeilencount, bookingdict, 
            context=context)
        return buchungserror, errorcount, thislog, partnererror, buchungszeilencount, bookingdict
   
    def buchungenHeaderDatev(self):
        """ Method that creates the Datev CSV Headerlione
        """
        buchung = []
        buchung.append(ustr("Währungskennung").encode("iso-8859-1"))
        buchung.append(ustr("Soll-/Haben-Kennzeichen").encode("iso-8859-1"))
        buchung.append(ustr("Umsatz (ohne Soll-/Haben-Kennzeichen)").encode("iso-8859-1"))
        buchung.append(ustr("BU-Schlüssel ").encode("iso-8859-1"))
        buchung.append(ustr("Gegenkonto (ohne BU-Schlüssel)").encode("iso-8859-1"))
        buchung.append(ustr("Belegfeld 1").encode("iso-8859-1"))
        buchung.append(ustr("Belegfeld 2").encode("iso-8859-1"))
        buchung.append(ustr("Datum").encode("iso-8859-1"))
        buchung.append(ustr("Konto").encode("iso-8859-1"))
        buchung.append(ustr("Kostfeld 1").encode("iso-8859-1"))
        buchung.append(ustr("Kostfeld 2").encode("iso-8859-1"))
        buchung.append(ustr("Kostmenge").encode("iso-8859-1"))
        buchung.append(ustr("Skonto").encode("iso-8859-1"))
        buchung.append(ustr("Buchungstext").encode("iso-8859-1"))
        buchung.append(ustr("EU-Land und UStID").encode("iso-8859-1"))
        buchung.append(ustr("EU-Steuersatz").encode("iso-8859-1"))
        buchung.append(ustr("Basiswährungsbetrag").encode("iso-8859-1"))
        buchung.append(ustr("Basiswährungskennung").encode("iso-8859-1"))
        buchung.append(ustr("Kurs").encode("iso-8859-1"))
        return buchung

    def buchungenCreateDatev(self, datevdict):
        """Method that creates the datev csv moveline
        """
        buchung = []
        buchung.append(datevdict['Waehrung'].encode("iso-8859-1"))
        buchung.append(datevdict['Sollhaben'].encode("iso-8859-1"))
        buchung.append(datevdict['Umsatz'].encode("iso-8859-1"))
        if datevdict['Buschluessel'] == '0':
            datevdict['Buschluessel'] = ''
        buchung.append(datevdict['Buschluessel'].encode("iso-8859-1"))
        buchung.append(datevdict['Gegenkonto'].encode("iso-8859-1"))
        datevdict['Beleg1'] = self.replace_non_ascii_characters(datevdict['Beleg1'])
        buchung.append(datevdict['Beleg1'].encode("iso-8859-1"))
        buchung.append(datevdict['Beleg2'].encode("iso-8859-1"))
        buchung.append(datevdict['Datum'].encode("iso-8859-1"))
        buchung.append(datevdict['Konto'] and datevdict['Konto'].encode("iso-8859-1") or 'NOTFILLED')
        buchung.append(datevdict['Kost1'].encode("iso-8859-1"))
        buchung.append(datevdict['Kost2'].encode("iso-8859-1"))
        buchung.append(datevdict['Kostmenge'].encode("iso-8859-1"))
        buchung.append(datevdict['Skonto'].encode("iso-8859-1"))
        datevdict['Buchungstext'] = datevdict['Buchungstext'][0:30]
        datevdict['Buchungstext'] = self.replace_non_ascii_characters(datevdict['Buchungstext'])
        buchung.append(datevdict['Buchungstext'].encode("iso-8859-1"))
        buchung.append(datevdict['EulandUSTID'].encode("iso-8859-1"))
        buchung.append(datevdict['EUSteuer'].encode("iso-8859-1"))
        buchung.append(datevdict['Basiswaehrungsbetrag'].encode("iso-8859-1"))
        buchung.append(datevdict['Basiswaehrungskennung'].encode("iso-8859-1"))
        buchung.append(datevdict['Kurs'].encode("iso-8859-1"))
        return buchung

ecofi()
