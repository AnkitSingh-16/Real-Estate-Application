from odoo import api, fields, models, exceptions
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer Model"
    _order = "price desc"

    price = fields.Float('Price')
    status = fields.Selection(
        [
            ('accepted', 'Accepted'), 
            ('refused', 'Refused'), 
        ],
        string='Status'
    )
    validity = fields.Integer('Validity (Days)', default = 7)
    date_deadline = fields.Date(
        'Deadline',
        compute = "_compute_date_deadline",
        inverse = "_inverse_date_deadline"
    )
    partner_id = fields.Many2one('res.partner', string = 'Partner',required = False,  default=lambda self: self.env.user)
    property_id = fields.Many2one('estate.property', required = False)
    property_type_id = fields.Many2one(related='property_id.property_type_id', string='Property Type', store=True)

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date and record.validity:
                record.date_deadline = record.create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days

    def accept_offer(self):
        for offer in self:
            offer.status = 'accepted'
            offer.property_id.buyer_id=offer.partner_id
            offer.property_id.selling_price=offer.price
            other_offers = self.search([('property_id', '=', offer.property_id.id), ('id', '!=', offer.id)])
            other_offers.write({'status': 'refused'})
            if offer.property_id.expected_price > 0:
                if offer.price < 0.9 * offer.property_id.expected_price:
                    raise models.ValidationError(("Selling price cannot be lower than 90% of the expected price."))
            offer.property_id.status = 'offer_accepted'

    def refuse_offer(self):
        self.status = 'refused'
    
    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        if property_id:
            property_record = self.env['estate.property'].browse(property_id)
            property_record.write({'status': 'offer_recieved'})
        
        existing_offers = self.search([('property_id', '=', property_id)])
        for offer in existing_offers:
            if vals.get('price') < offer.price:
                raise exceptions.ValidationError("The offer amount cannot be lower than the existing offer amount of %.2f." % offer.price)
        
        return super(EstatePropertyOffer, self).create(vals)

    _sql_constraints = [
        ('price_positive', 'CHECK(price > 0)', 'Offer price must be strictly positive.'),
    ]
