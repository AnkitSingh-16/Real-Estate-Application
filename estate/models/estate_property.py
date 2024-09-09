from odoo import api, fields, models, exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from .estate_property_type import EstatePropertyType
from .estate_property_tag import EstatePropertyTag
from .estate_property_offer import EstatePropertyOffer


class EstateProperty(models.Model):
    _name = "estate.property"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Estate Model"
    _order = "id desc"

    sequence = fields.Char(string='Sequence', readonly=True)
    name = fields.Char('Title', required=True)
    user_id = fields.Many2one('res.users', string='Salesperson',  default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', default=lambda self: self.env.user )
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Available From', copy = False, default=lambda self: datetime.now() + timedelta(days=90))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly = True, copy = False ) 
    bedrooms = fields.Integer('Bedrooms', default = 2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        string='Garden Orientation',
    )
    status = fields.Selection(
        [('new', 'New'), 
        ('offer_recieved', 'Offer Recived'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'), ('canceled', 'Canceled')],
        string='Status', default = 'new'
    )
    active = fields.Boolean('Active', default = True)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", inverse_name='property_id' )
    total_area = fields.Integer('Total Area', compute = "_compute_total_area")
    best_price = fields.Integer('Best Offer', compute = "_compute_best_price" )
    image = fields.Binary("Image", help="Select image here")

    def unlink(self):
        for record in self:
            if record.status not in ('new', 'canceled'):
                raise exceptions.ValidationError("Only New or Canceled state property can be deleted.")
        return super(EstateProperty, self).unlink()

    def create(self, vals):
        if isinstance(vals, list):
            for val in vals:
                if val.get('sequence', '/') == '/':
                    val['sequence'] = self.env['ir.sequence'].next_by_code('estate.property.sequence') or '/'
        else:
            if vals.get('sequence', '/') == '/':
                vals['sequence'] = self.env['ir.sequence'].next_by_code('estate.property.sequence') or '/'
        return super(EstateProperty, self).create(vals)

    # handler for computing the total area
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area  = record.living_area + record.garden_area

    # handler for computing the best price from existing price
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    # handler for setting the garden area and garden orientation automatically when garden is marked
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = "north"
        else :
            self.garden_area = False
            self.garden_orientation = False 

    # handler for sold and cancel button
    def _check_status(self, target_status):
        if self.status == target_status:
            raise UserError(f"The property is already {target_status}.")
    
    def action_cancel(self):
        self._check_status('sold')
        self.status = 'canceled'
    
    
    def action_sold(self):
        self._check_status('canceled')
        self.status = 'sold'

    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', 'Expected price must be strictly positive.'),
        ('selling_price_positive', 'CHECK(selling_price >= 0)', 'Selling price must be positive.'),
    ]
