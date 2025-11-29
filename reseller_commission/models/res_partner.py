from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Checkbox to identify reseller
    is_reseller = fields.Boolean(
        string="Is Reseller",
        help="Enable if this partner acts as a reseller and earns commissions."
    )

    # Commission settlements linked to this reseller
    commission_ids = fields.One2many(
        'commission.settlement',
        'reseller_id',
        string="Commission Settlements"
    )


    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        '''
        To Search With Other Fields Except the name field
        '''
        domain = domain or []
        if name:
            domain = ['|', '|',
                      ('name', operator, name),
                      ('email', operator, name),
                      ('phone', operator, name)
                      ] + domain

        return self._search(domain , limit=limit , order=order , access_rights_uid=self.env.uid)


