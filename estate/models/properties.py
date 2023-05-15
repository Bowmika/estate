from odoo import _, models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError,ValidationError


class Properties(models.Model):
    _name = "properties.properties"
    # button:the button is to view.when we select sold and save;after that you click the
    # cancel mean the user error must be popup.this is the condition of the button

    @api.constrains('expected_price', 'selling_price')
    def check_selling_price(self):
        for record in self:
            if record.selling_price > 0 and record.selling_price < 0.9 * record.expected_price:
                raise ValidationError("Selling price cannot be lower than 90% of expected price!")

    def action_sold(self):
        if self.stage == 'cancel':
            raise UserError("Cancel properties cannot be Sold")
        else:
            self.stage = 'sold'
            self.write({
                'status_bar': 'sold'
            })

    def action_cancel(self):
        if self.stage == 'sold':
            raise UserError("Sold properties cannot be Cancel")
        else:
            self.stage = 'cancel'

    # area calculation:In the depends on we calculate the living area and garden area
    @api.depends('living_area', 'garden_area')
    def compute_total_area(self):
        for rec in self:
            rec.total_area = 0
            rec.total_area = rec.living_area + rec.garden_area

    # USER ERROR: In this the Constraints wants to declare that the excepted price must be
    # in positive;if the expected price is negative the error raise

    @api.constrains('excepted_price')
    def _constraints_excepted_price(self):
        for record in self:
            if record.excepted_price < 0:
                raise UserError(_("The Excepted Price Must Be In Positive!"))

    # user call: When we call
    @api.model
    def _get_default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    @api.model
    def _get_default_buyer(self):
        return self.env.context.get('buyer_id', self.env.user.id)

    # when the garden area is 10 or 10 below the orientation must be arrived in given below code
    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.orientation = 'north'
        else:
            self.garden_area = 0
            self.orientation = False


    # button to refused and acceptable
    def action_acceptable(self):
        for bb in self:
            bb.status = 'acceptable'

    def action_refused(self):
        for bb in self:
            bb.status = 'refused'


    def unlink(self):
        for property in self:
            if property.stage not in ['new', 'cancel']:
                raise UserError("You cannot delete a property that is not in the 'New' or 'cancel' state.")
            return super(Properties, self).unlink()

    # Goal: at the end of this section, it will not be possible to accept an offer lower than 90 % of the expected price.


    name= fields.Char(string="Property Name")
    property_type= fields.Many2one("properties.types", string="property_type")
    post_code= fields.Char(string="Post Code")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    available_price = fields.Float(string="Available price")
    expected_price= fields.Float(string="Expected price")
    best_offer = fields.Char(string="Best_Offer")
    selling_price = fields.Float(string="Selling Price")
    description = fields.Char(string="Description")
    bedrooms = fields.Char(string="Bedrooms")
    living_area= fields.Integer(string="Living Area")
    face_des = fields.Char(string="Face Des")
    garage = fields.Char(string="Garage")
    garden = fields.Float(string='Garden')
    garden_area = fields.Boolean(string="Garden Area")
    total_area = fields.Integer(string="Total Area", compute="compute_total_area")
    offers = fields.Integer(string="Offers")
    other_info =fields.Char(string="Other Info")
    tags_ids = fields.Many2many("properties.tags", string="Tags")
    color = fields.Integer(string="Color")
    offer_ids = fields.One2many('offer.offer', 'properties_id', string='Properties')
    user_id = fields.Many2one('res.users', string='Sales Man', default=_get_default_user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', default=_get_default_buyer)
    orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string='Orientation')
    stage = fields.Selection([
        ('new', 'new'),
        ('sold', 'Sold'),
        ('cancel', 'Cancel'),
    ], string='stage',
        default='new',
        track_visibility='onchange')

    status_bar = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_acceptable', 'Offer Acceptable'),
        ('sold', 'Sold'),
    ], string='status', default="new")

    status = fields.Selection([
        ('acceptable', 'Acceptable'),
        ('refused', 'Refused'),
    ], string='status')


class Offer(models.Model):
    _name = 'offer.offer'

    # In the property offer model,
    # the validity date should be computed and can be updated
    @api.depends('validity')
    def _compute_validity_date(self):
        for rec in self:
            rec.deadline = fields.Date.today() + timedelta(days=rec.validity)

    # this is the method used to inverse the value

    def _set_deadline(self):
        for rec in self:
            rec.validity = (rec.deadline - fields.Date.today()).days

    # this onchange method that maybe we used to add the days to the deadline
    @api.onchange('validity')
    def onchange_validity_days(self):
        self.deadline = fields.Date.today() + timedelta(days=self.validity)

    # In this function,that when we click the button;the selling price,buyer_id,status bar must be change automatically fill
    def action_acceptable(self):
        for record in self:
            self.status = 'acceptable'
            for rec in record.properties_id:
                if self.status == 'acceptable':
                    rec.write({
                        'selling_price': self.price,
                        'buyer_id': self.partner_id.id,
                        'status_bar': 'offer_acceptable'
                    })

    # # In this function,that when we click the button;the selling price,buyer_id,status bar
    # # must be change automatically wants to invisible
    def action_refused(self):
        for record in self:
            for rec in record.properties_id:
                self.status = 'refused'
                if self.status == 'refused':
                    rec.write({
                        'selling_price': 0,
                        'buyer_id': [('buyer_id', '=', '')],
                        'status_bar': 'offer_received'
                    })

            raise exceptions.ValidationError("The offer price cannot be lower than an existing offer.")

    @api.model
    def create(self, vals):
        properties_id = vals.get('properties_id')
        price = vals.get('price')

        existing_offers = self.search([('properties_id', '=', properties_id)])
        if existing_offers and any(price < offer.price for offer in existing_offers):
            raise ValidationError("The offer price cannot be lower than an existing offer.")

        offer = super(Offer, self).create(vals)
        if offer.properties_id:
            offer.properties_id.status_bar = 'offer_received'
        return offer




    properties_id = fields.Many2one('properties.properties', string='properties')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one('res.partner')
    validity = fields.Integer(string='validity(days)')
    deadline = fields.Date(string='Deadline', compute='_compute_validity_date')
    status = fields.Selection([
      ('acceptable', 'Acceptable'),
      ('refused', 'Refused'),
    ], string='status')
    properties_type_id = fields.Many2one(related='properties_id.property_type', string='Type')
