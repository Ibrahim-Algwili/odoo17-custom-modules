import datetime
from email.policy import default
import logging
from datetime import date

from charset_normalizer.utils import is_latin
import requests

_logger = logging.getLogger(__name__)
from odoo import models , fields , api
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute
from datetime import timedelta


class Property(models.Model) :
    _name = 'property'
    _description = 'Property'
    _inherit = ['mail.thread' , 'mail.activity.mixin']


    # required default is (False)
    name = fields.Char(string="Name" , required=True , size=20 , translate=True)
    ref = fields.Char(default="New" , readonly=1)
    description = fields.Text(tracking=1)
    postcode = fields.Char(required=1 )
    date_availability = fields.Date(tracking=1)
    expected_selling_date = fields.Date(tracking=1)
    is_late = fields.Boolean()
    expected_price = fields.Float(digits=(0,2)) # how many digits after the (.)
    selling_price = fields.Float(digits=(0,2))
    diff = fields.Float(compute="_compute_diff" , readonly=1) # readonly (1 by default with compute)
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean(groups="app_one.property_manager_group")
    garden = fields.Boolean(required=1)
    garden_area = fields.Integer()
    file = fields.Binary(string="file" , attachment="True")
    garden_orientation = fields.Selection([
        ('north' , 'North'),
        ('south' , 'South'),
        ('east'  , 'East'),
        ('west'  , 'West')
    ] , default='west')

    create_time = fields.Datetime(default=fields.Datetime.now())
    next_time = fields.Datetime(compute='_compute_next_time')

    # Relational Fields (will added in the DB as foreign key)
    # Relation (M2O)
    owner_id = fields.Many2one('owner')

    # Relation (M2M)
    tag_ids = fields.Many2many('tag')

    # Related Fields
    owner_address = fields.Char(related="owner_id.address" , readonly=0)
    owner_phone = fields.Char(related="owner_id.phone" , readonly=1)

    # State Field
    state = fields.Selection([
        ('draft' , 'Draft'),
        ('pending' , 'Pending'),
        ('sold' , 'Sold'),
        ('closed' , 'Closed')
    ] , default='draft')


    # Relation with property.line
    line_ids = fields.One2many('property.line' , 'property_id')

    active = fields.Boolean(default=True) # this used for Archiving

    #Constraints on the Data Tier
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'This name is Exist'),
    ]


    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else :
                rec.next_time = False

    # -- Difference Between Expected/Selling Price
    @api.depends('expected_price' , 'selling_price' , 'owner_id.phone')
    def _compute_diff(self):
        '''
        will compute on this method
        after updating any of these fields
        becuse of the (depends Decorator)
        accepting all fields (view fields , model fields , relational fields)
        '''
        for rec in self:
            print(rec)
            print('inside _compute_diff Method')
            difference = rec.expected_price - rec.selling_price
            rec.diff = difference

    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        '''
        will print the text
        after updating this field
        becuse of the (onchange Decorator)
        but (it's just accepting view fields)
        '''
        for rec in self :
            print(rec)
            print('inside _onchange_expected_price Method')
            if rec.expected_price < 0 :
                return {
                    'warning' : {'title'   : 'warning',
                                 'message' : 'Negetive Number',
                                 'type'    : 'notification'}
                }


    # check this logic constraint on every record
    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero (self) :
        '''
        Constraints on Logic Tier
        (on bedrooms to check if it's zero)
        you need for loop if it's recordset more than one row
        but here it's not but we used for loop
        '''
        for rec in self :
            if rec.bedrooms == 0 :
                raise ValidationError('Please Add Valid number of bedrooms')


    # -- State Actions --
    def action_draft(self):
        for rec in self :
            print('inside draft action')
            rec.create_history_record(rec.state , 'draft')
            rec.state = 'draft'


    def action_pending(self):
        for rec in self :
            print('inside pending action')
            # it's the same as (rec.state)
            rec.create_history_record(rec.state, 'pending')
            rec.write({
                'state' : 'pending'
            })


    def action_sold(self):
        for rec in self :
            print('inside sold action')
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'


    def action_closed(self):
        for rec in self:
            print(f'Setting record {rec.name} to closed')
            rec.state = 'closed'  # أو rec.write({'state': 'closed'})



    def check_expected_selling_date(self) :
        # _logger.info('inside check_expected_selling_date')
        print(self)
        '''
        cron job when calling the Method 
        the self doesn't have any ids for the records (empty)
        it's refering to the model it self (property) 
        don't have to loop on records
        '''
        property_ids = self.search([]) # this line to return all the records with search Method
        print(property_ids)

        for rec in property_ids :
            if rec.expected_selling_date and rec.expected_selling_date < fields.date.today() :
                rec.is_late = True


    def action(self):
        # Search Domain
        print(self.env['property'].search([ '|',
            ('name' , 'like' , 'Property') ,
            ('postcode' , 'in' , ['21','22','23'])
        ]))


    def Env_action(self):

        # create
        print(self.env['owner'].create({
            'name'  : 'ali Khalefa',
            'phone' : '010000230'
        }))

        # search
        print(self.env['owner'].search([]))

        # User Details
        print(self.env)
        print(self.env.user.login)
        print(self.env.user.name)
        print(self.env.user.id)
        print(self.env.uid) # same like user.id
        # Company Details
        print(self.env.company.name)
        print(self.env.company.id)

        print(self.env.context)

        print(self.env.context)

        print(self.env.cr) # Cursor







    # CRUD Operations (Create , Read , Update , Delete)

    @api.model_create_multi
    def create(self, vals):
        # res = super(Property , self).create(vals)
        res = super().create(vals)
        # Logic
        # logic for the sequence
        if res.ref == 'New' :
            res.ref = self.env['ir.sequence'].next_by_code('property_seq')

        return res

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        res = super()._search(domain, offset=0, limit=None, order=None, access_rights_uid=None)
        # Logic
        print("inside _search Method")
        return res

    def write(self, vals):
        res = super().write(vals)
        # Logic
        print("inside write Method")
        return res


    def unlink(self):
        res = super().unlink()
        # Logic
        print("inside unlink Method")
        return res



    # ---- History logic Handling ------

    def create_history_record(self , old_state , new_state , reason=""):
        for rec in self:
            rec.env['property.history'].create({
                'user_id' : rec.env.uid,
                'property_id' : rec.id,
                'old_state'   : old_state,
                'new_state'   : new_state,
                'reason'      : reason or "",
                'line_ids'    : [(0 , 0 , {'description': line.description, 'area' : line.area }) for line in rec.line_ids] # this line is so important (magic or command tuple)
            })

    # ---- Change State Wizard ----
    def action_open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id' : self.id}
        return action


    # ------ Action For Smart Button (open owner form) -------
    def action_open_related_owner(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.owner_action') # to get the action id from the owner xml view
        view_id = self.env.ref('app_one.owner_view_Form').id # get the form view id
        action['res_id'] = self.owner_id.id
        action['views'] = [[view_id , 'form']]

        return action


    # -- Integrate with endpoint api --
    def get_properties(self):
        payload = dict({})
        try:
            response = requests.get('http://localhost:8069/v1/properties/filter' , data=payload )

            if response.status_code == 200 :
                print("successfully!")
            else :
                print("fail!")

        except Exception as error:
            raise ValidationError(str(error))

        print(response) # response 200 if success
        print(response.status_code) # response 200 if success
        print(response.content) # data in json



class PropertyLine(models.Model) :
    _name = 'property.line'

    property_id = fields.Many2one('property')
    area = fields.Float()
    description = fields.Char()