from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag Model"
    _order = "name"

    name = fields.Char( 'Property Tag', required=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('property_tag', 'UNIQUE(name)', 'Property tag must be unique.'),
    ]
