from odoo import models, fields,api


class PropertiesTypes(models.Model):
    _name = "properties.types"

    _sql_constraints = [
        ('name', 'unique (name)', 'The property type always in unique !!!')
    ]

    def action_properties_types(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Offers',
            'res_model': 'offer.offer',
            'view_mode': 'tree',
            'domain': "[('properties_type_id', '=', active_id)]",
            'context': "{'create': False}"
        }

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for properties_type in self:
            properties_type.offer_count = len(properties_type.offer_ids)

    name = fields.Char(string="Name")
    properties_ids = fields.One2many('type.type', 'properties_types_id', string='Property')
    offer_count = fields.Integer(string='Offer Count', compute='_compute_offer_count')
    offer_ids = fields.One2many('offer.offer', 'properties_type_id', string='Offers')


class TypeType(models.Model):
    _name = "type.type"

    properties_types_id = fields.Many2one('properties.types', string="Properties",)
    properties_id = fields.Many2one('properties.properties', string='Properties', domain="[('property_type', '=', properties_types_id)]")
    expected_price = fields.Float(string="Expected Price")
    status = fields.Char(string="Status")
