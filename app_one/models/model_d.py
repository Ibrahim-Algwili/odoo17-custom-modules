from odoo import models


class ModelD(models.Model) : # Model (the normal Model)
    # ORM will do mapping to this name as a Table in the DB
    _name = 'model.d' # table name (replace . with _ )
    _log_access = False
