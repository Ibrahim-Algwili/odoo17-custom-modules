import json
import logging
import math
from urllib.parse import parse_qs

from odoo import http
from odoo.http import Response, request

_logger = logging.getLogger(__name__)

# ---------- Valid and inValid Response Structure -----------

def valid_response(data , status , pagination_info) :
    response_body = {
        "message": "Successfull!!" ,
        "data" : data ,
    }
    if pagination_info :
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body , status=status)


def invalid_response(error , status) :
    response_body = {
        "error" : error ,
    }
    return request.make_json_response(response_body , status=status)



class PropertyApi(http.Controller):


    @http.route('/v1/property/query', type='json', auth='none', methods=['POST'], csrf=False)
    def post_property_query(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        if not vals.get('name'):
            return request.make_json_response({
                "message": "Name is Required"
            }, status=400)
        try:

            # -- using Query --
            cr = request.env.cr
            columns = ', '.join(vals.keys()) # ---> name , postcode, ....
            values  = ', '.join(['%s'] * len(vals)) # ---> '%s' , '%s' , ...
            query = f"""insert into property ({columns}) values ({values}) RETURNING id , name , postcode"""
            cr.execute(query , tuple(vals.values()))
            res = cr.fetchone()
            print(res)

            if res:
                return [{
                    "message": "Property has been created succsessfully",
                    "id": res[0],
                    "name": res[1],
                    "postcode": res[2],
                } ]
        except Exception as error:
            return request.make_json_response({
                "message": error
            }, status=400)



    @http.route('/v1/property/json', type='json', auth='none', methods=['POST'], csrf=False)
    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        if not vals.get('name') :
            return request.make_json_response({
                "message": "Name is Required"
            }, status=400)
        try:
            res = request.env['property'].sudo().create(vals)
            if res:
                return  [{
                    "message" : "Property has been created succsessfully",
                    "id" : res.id,
                    "name" : res.name
                }]
        except Exception as error :
            return request.make_json_response({
                "message": error
            }, status=400)


    @http.route("/v1/property/<int:property_id>" , methods=['PUT'] , type="http" , auth="none" , csrf=False)
    def update_property(self , property_id):
        try:
            property_id = request.env['property'].sudo().search([('id' , '=' , property_id)] , limit=1)

            if not property_id:
                return request.make_json_response({
                    "message": "ID doesn't Exist!!"
                }, status=400)
            args = request.httprequest.data.decode()
            vals = json.loads(args)

            property_id.write(vals)

            return request.make_json_response({
                    "message": "Property has been Updated succsessfully",
                    "id": property_id.id,
                    "name": property_id.name
                }, status=200)
        except Exception as error:
            return request.make_json_response({
                "message": str(error)
            }, status=400)

    @http.route("/v1/property/del/<int:property_id>", methods=['DELETE'], type="http", auth='none', csrf=False)
    def del_record(self, property_id):
        try:
            # البحث عن السجل
            record = request.env['property'].sudo().search([('id', '=', property_id)], limit=1)

            if not record:
                return request.make_json_response({
                    "message": "No record found with this ID"
                }, status=404)

            # حفظ id قبل الحذف
            record_id = record.id
            record.unlink()

            return request.make_json_response({
                "id": record_id,
                "message": "Property Deleted Successfully!"
            }, status=200)

        except Exception as error:
            return request.make_json_response({
                "message": str(error)
            }, status=500)

    @http.route("/v1/property/read/<int:property_id>", methods=["GET"], type="http", auth="none", csrf=False)
    def read_record(self, property_id):
        try:
            record = request.env['property'].sudo().search([('id', '=', property_id)], limit=1)
            if not record:
                return invalid_response(
                    "No record found with this ID" , status=404)

            data = record.read(['name' , 'ref' , 'postcode' , 'bedrooms' , 'garden_orientation'])[0]

            return valid_response({
                "record": data
            }, status=200)


        except Exception as error:
            return invalid_response({
                "error": str(error)
            }, status=500)

    @http.route("/v1/properties", methods=["GET"], type="http", auth="none", csrf=False)
    def read_record_list(self):
        try:
            property_ids = request.env['property'].sudo().search([]) # get all records (no domain)
            if not property_ids:
                return request.make_json_response({
                    "error": "No records in the Table"
                }, status=404)

            return request.make_json_response([ {
                "id" : property_id.id,
                "name" : property_id.name,
                "ref" : property_id.ref,
                "description" : property_id.description,
                "bedrooms" : property_id.bedrooms,
            } for property_id in property_ids], status=200)

        except Exception as error:
            return request.make_json_response({
                "error": str(error)
            }, status=500)


    @http.route("/v1/properties/filter", methods=["GET"], type="http", auth="none", csrf=False)
    def get_records_with_filters(self):
        try:
            # params = request.params
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            property_domain = []

            page = offset = None
            limit = 5

            if params:
                if params.get('limit') :
                    limit = int(params.get('limit')[0])

                if params.get('page') :
                    page = int(params.get('page')[0])

            if page:
                offset = (page * limit) - limit

            if params.get('state'):
                property_domain += [('state' , '=' , params.get('state')[0])]


            property_ids = request.env['property'].sudo().search(
                property_domain,
                offset = offset,
                limit = limit,
                order = 'id desc',
            )

            property_count = request.env['property'].sudo().search_count(property_domain)

            print(property_ids)
            print(f"property count : ({property_count})")
            print(page)
            print(offset)
            print(limit)

            if not property_ids:
                return request.make_json_response({
                    "error": "No records in the Table"
                }, status=404)

            return valid_response([ {
                "id" : property_id.id,
                "name" : property_id.name,
                "ref" : property_id.ref,
                "description" : property_id.description,
                "bedrooms" : property_id.bedrooms,
                "state" : property_id.state,
            } for property_id in property_ids], pagination_info={
                'page'  : page if page else 1,
                'limit' : limit,
                'pages' : math.ceil(property_count / limit) if limit else 1,
                'count' : property_count
            } , status=200)

        except Exception as error:
            return invalid_response({
                "error": str(error)
            }, status=500)

