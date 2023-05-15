from odoo import models, fields


class PropertiesTags(models.Model):
    _name = "properties.tags"

    name= fields.Char(string="Name")
    color = fields.Integer(string="Color")
