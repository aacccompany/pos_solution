# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models
class ResCompany(models.Model):
    _inherit = 'res.company'
    pos_solution_secret_key = fields.Char("Secret Key")
    pos_solution_auth_key = fields.Char("Auth Key")
    pos_solution_api_key = fields.Char("API Key")
    pos_solution_merchant_id = fields.Char("Merchant Id")
    
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    pos_solution_secret_key = fields.Char("Secret Key", config_parameter='pos_solution.secret_key')
    pos_solution_auth_key = fields.Char("Auth Key", config_parameter='pos_solution.auth_key')
    pos_solution_api_key = fields.Char("API Key", config_parameter='pos_solution.api_key')
    pos_solution_merchant_id = fields.Char("Merchant Id", config_parameter='pos_solution.merchant')
