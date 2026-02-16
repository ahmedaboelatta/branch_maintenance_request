# -*- coding: utf-8 -*-
from odoo import models, fields


class EquipmentCategory(models.Model):
    _name = 'branch_maintenance.category'
    _description = 'Equipment Category'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Category Name', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', tracking=True)
    Employee_phone = fields.Char(related='employee_id.work_phone', string='Employee Phone', readonly=1, tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name must be unique!'),
    ]
