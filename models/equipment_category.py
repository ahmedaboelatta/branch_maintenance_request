# -*- coding: utf-8 -*-
from odoo import models, fields


class EquipmentCategory(models.Model):
    _name = 'branch_maintenance.category'
    _description = 'Equipment Category'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Category Name', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    employee_id = fields.Many2one('res.partner', string='Employee Name', 
                                  domain="[('is_company', '=', False)]", tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name must be unique!'),
    ]
