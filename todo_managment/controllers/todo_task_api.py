import json
from crypt import methods

from idna import valid_label_length
from reportlab.lib.colors import limegreen

from . import response_api as response
import requests

from odoo import models, fields, api, http
from odoo.http import request
from ...app_one.controllers.property_api import invalid_response


def valid_respons(data , status):
    response_body = {
        'message' : 'Successfull!',
        'data' : data
    }

    return request.make_json_response(response_body , status=status)

def invalid_respons(message, status):
    response_body = {
        'error' : message
    }

    return request.make_json_response(response_body, status=status)

class TodoTaskApi(http.Controller) :

    @http.route("/api/task/create" , methods=['POST'] , type="http" , auth='none' , csrf=False)
    def api_create(self):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)

            if not vals.get('name') :
                return invalid_respons({
                    'message' : 'name is required'
                } , 400)

            if not vals.get('assign_to'):
                return invalid_respons({
                    'message': 'assign is required'
                }, 400)

            res = request.env['todo.task'].sudo().create(vals)

            return valid_respons({
                'name' : res.name ,
                'description' : res.description ,
                'assign_to' : res.assign_to.id ,
            } , 200)

        except Exception as error :
            return invalid_respons({
                'error' : str(error)
            } , 500)



    @http.route("/api/task/del/<int:task_id>" , methods=['DELETE'] , type="http" , auth='none' , csrf=False)
    def api_delete(self , task_id):
        try:

            record = request.env['todo.task'].sudo().search([('id' , '=' , task_id)] , limit=1)

            if not record :
                return valid_respons({
                    'message' : f'NO ID like this {record}'
                } , 400)

            del_id = record.id
            record.unlink()


            return valid_respons({
                f'ID {del_id}' : 'Has Been Deleted'
            } , 200)

        except Exception as error :
            return invalid_respons({
                'error' : str(error)
            } , 500)

    @http.route("/api/task/update/<int:task_id>", methods=['PUT'], type="http", auth='none', csrf=False)
    def api_update(self, task_id):
        try :
            args = request.httprequest.data.decode()
            vals = json.loads(args)

            record = request.env['todo.task'].sudo().search([('id' , '=' , task_id)] , limit=1)

            if not record :
                return invalid_respons({
                    'message': f'NO ID like this {record}'
                }, 400)

            if not vals.get('name') :
                return invalid_respons({
                    'message': f'Name is Required'
                }, 400)

            record.write(vals)

            return valid_respons(vals , 200)


        except Exception as error:
            return invalid_respons({
                'error': str(error)
            }, 500)


    @http.route("/api/task/read/<int:task_id>", methods=['GET'], type="http", auth='none', csrf=False)
    def api_read_record(self, task_id):
        try :
            record = request.env['todo.task'].sudo().search([('id' , '=' , task_id)] , limit=1)

            if not record:
                return invalid_respons({
                    'message': f'NO ID like this {record}'
                }, 400)


            data = record.read(['name' , 'description' , 'assign_to'])[0]

            return valid_respons(data , 200)

        except Exception as error:
            return invalid_respons({
                'error': str(error)
            }, 500)



    @http.route("/api/task/readlist", methods=['GET'], type="http", auth='none', csrf=False)
    def api_read_List(self):
        try:
            record = request.env['todo.task'].sudo().search([])
            print(record)

            if not record:
                return invalid_respons({
                    'message': f'NO ID like this {record}'
                }, 400)


            return valid_respons([{
                'name' : task_ids.name,
                'description' : task_ids.description,
                'assign_to' : task_ids.assign_to.name,
            } for task_ids in record ], 200)

        except Exception as error:
            return invalid_respons({
                'error': str(error)
            }, 500)
