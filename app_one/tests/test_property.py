from odoo import fields

from odoo.tests.common import TransactionCase, _logger


class TestProperty (TransactionCase) :

    def setUp(self , *args , **kwargs):
        super().setUp()

        self.property_01_record = self.env['property'].create({
            'ref' : 'PRT1000',
            'name' : 'Property 1000',
            'description' : 'Property 1000 descreption',
            'postcode' : '1010',
            'date_availability' : fields.datetime.today() ,
            'bedrooms' : 10,
            'expected_price' : 1000
        })

    def test_00_simple_check(self):
        # هذا الاختبار لا يعتمد على أي سجلات تم إنشاؤها
        self.assertTrue(True, "Simple boolean check")
        _logger.info("--- TEST 00 HAS EXECUTED ---")

    # ------- Test Cases ---------
    def test_01_property_values(self):
        property_id = self.property_01_record

        # checking if the values right or not
        self.assertRecordValues(property_id , [{
            'ref': 'PRT1000',
            'name': 'Property 1000',
            'description': 'Property 1000 descreption',
            'postcode': '1010',
            'date_availability': fields.datetime.today(),
            'bedrooms': 10,
            'expected_price': 1000,
        }])