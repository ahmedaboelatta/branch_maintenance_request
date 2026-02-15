# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _name = 'branch_maintenance.equipment'
    _description = 'Equipment Inventory'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Equipment Name', required=True, tracking=True)
    image_1920 = fields.Binary("Equipment Image")
    equipment_model_id = fields.Many2one('branch_maintenance.equipment.model', string='Equipment Model', tracking=True)
    category_id = fields.Many2one('branch_maintenance.category', string='Category', tracking=True)
    branch_id = fields.Many2one('branch_maintenance.branch', string='Branch', tracking=True)
    purchase_date = fields.Date(string='Purchase Date', tracking=True)
    serial_number = fields.Char(string='Serial Number', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    # Compute full name for display
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    @api.depends('name', 'serial_number')
    def _compute_display_name(self):
        for rec in self:
            if rec.serial_number:
                rec.display_name = f"{rec.name} ({rec.serial_number})"
            else:
                rec.display_name = rec.name

    _sql_constraints = [
        ('serial_number_unique', 'unique(serial_number)', 'Serial number must be unique!'),
    ]
