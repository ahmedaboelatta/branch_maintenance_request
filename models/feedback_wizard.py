# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MaintenanceFeedbackWizard(models.TransientModel):
    _name = 'branch_maintenance.feedback.wizard'
    _description = 'Maintenance Request Feedback Wizard'

    request_id = fields.Many2one('branch_maintenance.request', string='Maintenance Request', required=True)
    
    rating = fields.Selection([
        ('0', '0 Stars'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ], string='Service Rating', default='3', required=True)
    
    feedback = fields.Text(string='Feedback', placeholder='Share your experience with the service...', tracking=True)

    def action_submit_feedback_and_close(self):
        """Submit the feedback and close the maintenance request"""
        for wizard in self:
            if wizard.request_id.state != 'repaired':
                raise UserError(_('Request must be in Repaired state to be closed.'))
            
            # Update the request with rating and feedback
            wizard.request_id.write({
                'rating': int(wizard.rating),
                'rating_feedback': wizard.feedback,
                'state': 'closed',
                'closed_date': fields.Datetime.now()
            })
            
            # Post a message
            wizard.request_id.message_post(
                body=_('Request closed by branch user with rating: %s stars', wizard.rating)
            )
        
        return {'type': 'ir.actions.act_window_close'}
