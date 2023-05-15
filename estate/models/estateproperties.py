from odoo import models, fields


class estateproperties(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('properties.properties', 'user_id', string='Property')