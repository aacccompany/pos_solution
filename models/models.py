# -*- coding: utf-8 -*-

from odoo import models, fields, api
#import random
#import string
import json
import requests
import random


class PosSolution(models.Model):
    _name = 'pos.solution'
    _description = 'POS Payment QR Code'

    name = fields.Char()
    pos_ref = fields.Char(index=True)
    value = fields.Text()
    ref = fields.Char(index=True)
    value2 = fields.Float(compute="_value_pc", store=True)
    amount = fields.Float(default=0)
    description = fields.Text()
    solution_ref = fields.Text()
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, index=True,
        default='draft')

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

    @api.model
    def create(self, vals):
        #letters = string.ascii_uppercase
        #vals['ref'] = ''.join(random.choice(letters) for i in range(10))
        return super(PosSolution, self).create(vals)

    @api.model
    def get_pay_order(self, vals):
        orderId = vals['pos_ref']
        ref = "%0.12d" % random.randint(0, 999999999999)
        amount = "{:.2f}".format(vals['amount'])
        vals['ref'] = ref

        auth_key = self.env.company.pos_solution_auth_key
        merchant_id = self.env.company.pos_solution_merchant_id

        headers = {
            'Authorization': 'Basic {auth_key}'.format(auth_key=auth_key),
            'Content-Type': 'application/json'
        }
        url = "https://apis.paysolutions.asia/tep/api/v2/promptpay?merchantID={merchant_id}&productDetail={orderId}&customerEmail=wineoclock.erp@gmail.com&customerName=wineoclock&total={amount}&referenceNo={refNo}".format(
            orderId=orderId, merchant_id=merchant_id, amount=amount, refNo=ref)

        print(url)

        response = requests.post(
            url, data={}, headers=headers)

        records = self.search([('pos_ref', '=', vals['pos_ref'])])
        if len(records) > 0:
            record = records[0]
            record.write({"ref": vals['ref']})
        else:
            self.create(vals)
        return response.json()

    @api.model
    def check_solution_order(self, vals):
        count = self.search_count(
            [('pos_ref', '=', vals['pos_ref']), ('state', '=', 'paid')])
        return {"count": count}

    @api.model
    def toggle_from_webhook_solution_order(self, param):
        ref_key = param.get("refno")
        data = self.search([('ref', '=', ref_key)])
        if (len(data) == 0):
            return "failed"
        record = data[0]
        record.write({"state": "paid"})
        record.write({"solution_ref": param})
        return "success"
