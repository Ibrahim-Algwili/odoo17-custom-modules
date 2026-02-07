from odoo import http
from odoo.http import Response

class TestApi(http.Controller):

    @http.route('/api/test', type='json', auth='none', methods=['GET'], csrf=False)
    def test_endpoint(self):
        print("inside test_endpoint method")  # يظهر في الـ log أو الكونسول
        return Response("Hello from Odoo API!", status=200)
