# -*- coding: utf-8 -*-
from odoo import models, fields


class EquipmentModel(models.Model):
    _name = 'branch_maintenance.equipment.model'
    _description = 'Equipment Model/Type'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Model Name', required=True, tracking=True)
    manufacturer = fields.Char(string='Manufacturer', tracking=True)
    description = fields.Text(string='Description', tracking=True)
    category_id = fields.Many2one('branch_maintenance.category', string='Category', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Model name must be unique!'),
    ]
