from odoo import http
from odoo.http import request, route


class PosSolution(http.Controller):

    @http.route('/aacc_x_odoo/pos_solution_webhook', type='http', auth="public", csrf=False, cors="*")
    def get_json(self, path=None):
        result = request.env['pos.solution'].sudo(
        ).toggle_from_webhook_solution_order(request.params)
        return result
