from odoo import http
from odoo.http import request
from datetime import datetime

class PropertyWebsiteController(http.Controller):
    
    @http.route('/estate/<model("estate.property"):property>/', auth='public', website=True)
    def property(self, property):
        return http.request.render('estate.property_details', {
            'property': property
        })

    @http.route('/properties/', auth='public', website=True)
    def menu_page(self, page='1', list_after_date=None, **kw):
        Property = request.env['estate.property']
        page = int(page)
        offset = (page - 1) * 6

        domain = []
        if list_after_date:
            list_after_date = datetime.strptime(list_after_date, '%Y-%m-%d')
            domain.append(('create_date', '>=', list_after_date))

        properties = Property.sudo().search(domain, limit=6, offset=offset, order='create_date DESC')
        total_properties = Property.search_count([])
        total_pages = (total_properties + 5) // 6
        pager = {
            'prev_page': page - 1 if page > 1 else False,
            'next_page': page + 1 if page < total_pages else False,
            'page': page,
        }
        return http.request.render('estate.property_template', {
            'properties': properties,
            'pager': pager,
        })
