import datetime
from email.policy import default
import logging
from datetime import date

from charset_normalizer.utils import is_latin

_logger = logging.getLogger(__name__)
from odoo import models , fields , api
from odoo.exceptions import ValidationError
from odoo.tools.populate import compute


class PropertyHistory(models.Model) :
    _name = 'property.history'
    _description = 'Property History'

    user_id = fields.Many2one('res.users')
    property_id = fields.Many2one('property')
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()
    line_ids = fields.One2many('property.history.line' , 'history_id')



class PropertyHistoryLine(models.Model) :
    _name = 'property.history.line'

    history_id = fields.Many2one('property.history')
    area = fields.Float()
    description = fields.Char()