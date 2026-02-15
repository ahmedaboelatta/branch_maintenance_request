# -*- coding: utf-8 -*-
{
    'name': 'Branch Maintenance Request',
    'version': '18.0.1.0.0',
    'category': 'Services/Maintenance',
    'summary': 'Manage maintenance requests from branches',
    'description': """
Branch Maintenance Request Module
=================================

This module enables branches to submit maintenance requests for equipment,
streamlining communication between branch managers and the maintenance department.

Key Features:
- Branch management with location
- Equipment category management
- Priority levels (1-3 stars)
- Complete workflow tracking (Draft -> Submitted -> In Progress -> Repaired -> Closed)
- Auto-location fetching when branch is selected
- Service rating (1-5 stars) before closing
- Kanban and List views for easy management
- Pivot and Graph views for analytics
- Photo attachment support
- Automated notifications via Odoo Chatter
    """,
    'author': 'Ahmed Abo EL-Atta',
    'website': 'https://alezdhar.com/',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir.sequence.xml',
        'views/request_views.xml',
        'views/branch_views.xml',
        'views/category_views.xml',
        'views/equipment_model_views.xml',
        'views/equipment_views.xml',
        'views/feedback_wizard_views.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 100,
}
