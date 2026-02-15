# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MaintenanceRequest(models.Model):
    _name = 'branch_maintenance.request'
    _description = 'Branch Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('repaired', 'Repaired/Done'),
        ('closed', 'Closed'),
    ]

    def _default_employee(self):
        """Default employee is the current user's partner"""
        return self.env.user.partner_id.id if self.env.user.partner_id else False

    name = fields.Char(string='Request Number', readonly=True, copy=False, tracking=True)
    state = fields.Selection(selection=STATE_SELECTION, string='Status', default='draft', tracking=True,
                             group_expand='_read_group_state_ids')
    priority = fields.Selection([
        ('0', 'Low'),  # ستظهر 0 نجوم
        ('1', 'Medium'),  # ستظهر نجمة واحدة
        ('2', 'High'),  # ستظهر نجمتان
        ('3', 'Very High')  # ستظهر 3 نجوم ⭐⭐⭐
    ], string='Priority', default='1', tracking=True)
    
    # Request description
    description = fields.Text(string='Description', tracking=True)
    
    # Use new branch model instead of res.partner
    branch_id = fields.Many2one('branch_maintenance.branch', string='Branch', required=True, tracking=True)
    branch_location = fields.Char(string='Location', related='branch_id.location', readonly=True)
    
    # Equipment selection - user selects Equipment Type first, then Equipment filtered by type and branch
    equipment_id = fields.Many2one('branch_maintenance.equipment', string='Equipment Name', tracking=True)
    equipment_type = fields.Many2one('branch_maintenance.category', string='Equipment Type', tracking=True)
    
    # Employee field - defaults to current user
    employee_id = fields.Many2one('res.partner', string='Employee Name',
                                    domain="[('is_company', '=', False)]",
                                    default=_default_employee, tracking=True)

    # Mandatory photo attachment
    photo_ids = fields.Many2many('ir.attachment', string='Photos', required=True, tracking=True)
    
    technician_id = fields.Many2one('res.partner', string='Technician', domain="[('is_company', '=', False)]", tracking=True)
    
    rating = fields.Integer(string='Service Rating', help='Service rating 1-5 stars', tracking=True)
    rating_feedback = fields.Text(string='Feedback', tracking=True)
    
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    active = fields.Boolean('Active', default=True)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    submitted_date = fields.Datetime(string='Submitted Date', readonly=True)
    repaired_date = fields.Datetime(string='Repaired Date', readonly=True)
    closed_date = fields.Datetime(string='Closed Date', readonly=True)
    
    sla_hours = fields.Float(string='SLA (Hours)', compute='_compute_sla', store=True)
    total_hours = fields.Float(string='Total (Hours)', compute='_compute_total', store=True)

    def _read_group_state_ids(self, domain, order, groupby=None):
        """Helper method for group_expand to show all states in order"""
        # Return all state keys in the order defined in STATE_SELECTION
        return [key for key, val in self.STATE_SELECTION]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Generate sequence number if not provided or if it's empty/False
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('branch_maintenance.request')
        return super().create(vals_list)

    @api.depends('submitted_date', 'repaired_date')
    def _compute_sla(self):
        for req in self:
            if req.submitted_date and req.repaired_date:
                duration = req.repaired_date - req.submitted_date
                req.sla_hours = duration.total_seconds() / 3600
            else:
                req.sla_hours = 0

    @api.depends('create_date', 'closed_date')
    def _compute_total(self):
        for req in self:
            if req.create_date and req.closed_date:
                duration = req.closed_date - req.create_date
                req.total_hours = duration.total_seconds() / 3600
            else:
                req.total_hours = 0

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        """Clear equipment and category selection when branch changes"""
        self.equipment_type = False
        self.equipment_id = False
        self.employee_id = False

    @api.onchange('equipment_type')
    def _onchange_equipment_type(self):
        """Filter equipment based on selected branch and equipment type"""
        # Clear equipment selection when category changes
        self.equipment_id = False
        
        # Build domain for equipment
        domain = []
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        if self.equipment_type:
            domain.append(('category_id', '=', self.equipment_type.id))
        
        # Return domain for equipment field
        return {'domain': {'equipment_id': domain}}

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        """Auto-set employee when equipment is selected"""
        if self.equipment_id:
            # Auto-set employee from category's employee (leave empty if no employee in category)
            if self.equipment_id.category_id and self.equipment_id.category_id.employee_id:
                self.employee_id = self.equipment_id.category_id.employee_id.id
            else:
                self.employee_id = False

    def action_submit(self):
        for req in self:
            if req.state != 'draft':
                raise UserError(_('Only draft requests can be submitted.'))
            # Validate at least one photo is attached
            if not req.photo_ids:
                raise UserError(_('Please attach at least one photo of the equipment before submitting.'))
            req.write({'state': 'submitted', 'submitted_date': fields.Datetime.now()})
            req.message_post(body=_('Request submitted.'))

    def action_start_work(self):
        for req in self:
            if req.state not in ['submitted']:
                raise UserError(_('Request must be submitted to start work.'))
            req.write({'state': 'in_progress'})

    def action_mark_repaired(self):
        for req in self:
            if req.state not in ['in_progress']:
                raise UserError(_('Request must be in progress to mark repaired.'))
            req.write({'state': 'repaired', 'repaired_date': fields.Datetime.now()})

    def action_close_wizard(self):
        """Open the feedback wizard to close the request"""
        # Ensure we have exactly one record
        if len(self) != 1:
            raise UserError(_('Please select exactly one request to close.'))
        
        if self.state != 'repaired':
            raise UserError(_('Request must be in Repaired state to be closed.'))
        
        return {
            'name': _('Close Request with Feedback'),
            'type': 'ir.actions.act_window',
            'res_model': 'branch_maintenance.feedback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

    def action_reset_draft(self):
        for req in self:
            if req.state == 'closed':
                raise UserError(_('Closed requests cannot be reset.'))
            req.write({'state': 'draft', 'submitted_date': False, 'repaired_date': False, 'closed_date': False})
