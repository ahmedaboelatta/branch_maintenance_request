# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MaintenanceBranch(models.Model):
    _name = 'branch_maintenance.branch'
    _description = 'POS Maintenance Branch'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Branch Name', required=True, tracking=True)
    location = fields.Char(string='Location/Address', required=True, tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Branch name must be unique!'),
    ]
