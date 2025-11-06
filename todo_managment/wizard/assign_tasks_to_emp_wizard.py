from odoo import models , fields



class AssignTasks(models.TransientModel):
    _name = 'assign.tasks.to.emp.wizard'
    _description = 'Wizard to Assign Tasks to a User'


    partner_id = fields.Many2one('res.partner' , string='user' , required=1)

    def action_assign(self):
        # Get selected tasks from context
        active_ids = self.env.context.get('active_ids')
        tasks = self.env['todo.task'].browse(active_ids)

        for task in tasks:
            task.partner_id = self.partner_id.id

        return {'type': 'ir.actions.act_window_close'}