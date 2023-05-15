from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    property_id = fields.Many2many('properties.properties', string='Property', readonly=True, copy=False)