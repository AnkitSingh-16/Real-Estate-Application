from odoo import api, models

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        account_move_obj = self.env['account.move']
        for property_record in self:
            total_price = property_record.selling_price
            taxes = total_price * 0.06
            administrative_fees = 100.00
            
            invoice_lines = [
                (0, 0, {
                    'name': 'Property Sale',
                    'quantity': 1,
                    'price_unit': total_price,
                    'tax_ids': [(6, 0, [])],
                }),
                (0, 0, {
                    'name': 'Administrative Fees',
                    'quantity': 1,
                    'price_unit': administrative_fees,
                    'tax_ids': [(6, 0, [])]
                }),
            ]
            
            vals = {
                'partner_id': property_record.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
            }
            account_move = account_move_obj.create(vals)
        return super(EstateProperty, self).action_sold()
