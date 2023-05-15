from odoo import  fields, models
import logging

_logger = logging.getLogger(__name__)

class Properties (models.Model):
    _inherit = 'properties.properties'

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)

    def action_sold(self):
        res = super(Properties, self).action_sold()
        _logger.info('Property %s has been sold', self.name)

        # Create empty account move
        move = self.env['account.move'].create({
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'price_unit': self.selling_price * 0.06
            }), (0, 0, {
                'name': 'Administrative Fees',
                'price_unit': 100.0
            })]
        })
        _logger.info('Created invoice %s for property %s', move.name, self.name)

        return res

