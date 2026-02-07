import datetime
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime
from odoo.tools.populate import compute


class ToDoTask(models.Model):
    _name = 'todo.task'
    _description = 'To-Do App'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Task Name" , required=1 , help="Write Task Name")
    description = fields.Text(string="Description" , help="Full Description")
    due_date = fields.Date(string="Due Date" )
    partner_id = fields.Many2one('res.partner', string="Assigned To" , required=1 , ondelete="restrict")
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ], string="Status" , tracking=1)
    estimated_time = fields.One2many('todo.task.line' , 'todo_task_id')
    active = fields.Boolean(default=True)
    is_late = fields.Boolean(default=False)
    ref = fields.Char(default='New' , readonly=1 )




    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.ref == 'New':
                rec.ref = self.env['ir.sequence'].next_by_code('todo_seq')
        return records

    @api.constrains('due_date')
    def _check_assign_to(self):
        for rec in self:
            if not rec.partner_id :
                raise ValidationError("You must choose user to assign the task to !!")

    def check_due_date(self):
        today = fields.Date.today()
        records = self.search([])
        for rec in records:
            if rec.status not in ('completed', 'closed'):
                if rec.due_date and rec.due_date < today:
                    rec.is_late = True
                else:
                    rec.is_late = False
            else:

                rec.is_late = False
        print("✅ تم تحديث حالات المهام بناءً على التاريخ.")


    def action_completed(self):
        for rec in self :
            rec.sudo().write({'status' : 'completed'})

    def action_in_progress(self):
        for rec in self :
            rec.sudo().write({'status' : 'in_progress'})

    def action_new(self):
        for rec in self :
            rec.status = 'new'

    def action_closed(self):
        for rec in self :
            rec.status = 'closed'



        # ---- Change State Wizard ----

    def action_assign_tasks_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('todo_managment.window_action_wizard')
        action['context'] = {
            'active_model': 'todo.task',
            'active_ids': self.ids,
            'default_partner_id': False,  # optional default value
        }
        return action





    class TodoLine (models.Model):
        _name = "todo.task.line"

        t_description = fields.Text(string="Description" , required=1)
        time_taken = fields.Float(string="Duration (hours)" , required=1)
        todo_task_id = fields.Many2one('todo.task')