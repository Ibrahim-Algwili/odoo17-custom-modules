from ast import literal_eval
from odoo import http
from odoo.http import request
import io
import xlsxwriter


class XlsxPropertyReport(http.Controller):

    @http.route('/property/excel/report/<string:property_ids>',type='http',auth="user")
    def download_property_excel_report(self, property_ids):

        print(property_ids)

        # properyt_ids = list of ids of the records selected
        property_ids = request.env['property'].browse(literal_eval(property_ids)) # Converts The String To List
        print(property_ids)

        output = io.BytesIO() # To Store File in The Memory
        workbook = xlsxwriter.Workbook(output , {'in_memory':True}) # work book of the Excel File
        worksheet = workbook.add_worksheet(name="Properties") # A Sheet inside The WorkBook

        # First Row Header Format and Data Format
        header_format = workbook.add_format({'bold':True , 'bg_color':'gray' , 'border':1 , 'align':'center' })
        string_format = workbook.add_format({'border':1 , 'align':'center' })
        price_format = workbook.add_format({ 'num_format':'$##,##00.00' ,'border':1 , 'align':'center'})

        # Change Width of The Cell
        worksheet.set_column(0,0, 30)
        worksheet.set_column(0,2, 20)

        headers = ['Name' , 'Post Code' , 'Selling Price' , 'Garden'] # Header Labes

        for col_num,header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format) # (row, cloumn, Value_in_cell, format)


        # Accessing the data of records
        row_num = 1
        for property in property_ids:
            worksheet.write(row_num , 0 , property.name, string_format)
            worksheet.write(row_num , 1 , property.postcode, string_format)
            worksheet.write(row_num , 2 , property.selling_price, price_format)
            worksheet.write(row_num , 3 , 'YES' if property.garden else 'NO' , string_format)
            row_num += 1

        workbook.close()
        output.seek(0) # to Start Reading from The Begening

        file_name = 'Property Report.xlsx'

        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={file_name}'),
            ]
        )