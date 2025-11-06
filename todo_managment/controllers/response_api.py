import json
from crypt import methods

import requests

from odoo import models, fields, api
from odoo.addons.test_impex.tests.test_load import message
from odoo.http import request



def valid_response(data , status):
    response_body = {
        'message' : 'Successfull!',
        'data' : data
    }

    return request.make_json_response(response_body , status=status)

def invalid_response(message, status):
    response_body = {
        'Message' : message
    }

    return request.make_json_response(response_body, status=status)
