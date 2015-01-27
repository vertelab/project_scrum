# -*- coding: utf-8 -*-

import fields
from tools.translate import _
import re
import time
import tools
from datetime import datetime
from dateutil.relativedelta import relativedelta

class project_scrum_sprint(osv.osv):
    _name = 'project.scrum.sprint'
    _description = 'Project Scrum Sprint'
    _order = 'date_start desc'
    def _compute(self):
        self.progress = 42.0

    name = fields.char('Sprint Name', required=True, size=64),
    date_start = fields.date('Starting Date', required=True, default = fields.date.now()),
    date_stop = fields.date('Ending Date', required=True),
    project_id = fields.many2one('project.project', 'Project', required=True, domain=[('scrum','=',1)], help="If you have [?] in the project name, it means there are no analytic account linked to this project."),
    product_owner_id = fields.many2one('res.users', 'Product Owner', required=True,help="The person who is responsible for the product"),
    scrum_master_id = fields.many2one('res.users', 'Scrum Master', required=True,help="The person who is maintains the processes for the product"),
    # meeting_ids = fields.one2many('project.scrum.meeting', 'sprint_id', 'Daily Scrum'),
    review = fields.text('Sprint Review'),
    retrospective = fields.text('Sprint Retrospective'),
    # backlog_ids = fields.one2many('project.scrum.product.backlog', 'sprint_id', 'Sprint Backlog'),
    progress = fields.Float(compute="_compute", group_operator="avg", type='float', multi="progress", string='Progress (0-100)', help="Computed as: Time Spent / Total Time."),
    effective_hours = fields.function(_compute, multi="effective_hours", string='Effective hours', help="Computed using the sum of the task work done."),
    expected_hours = fields.function(_compute, multi="expected_hours", string='Planned Hours', help='Estimated time to do the task.'),
    state = fields.selection([('draft','Draft'),('open','Open'),('pending','Pending'),('cancel','Cancelled'),('done','Done')], 'State', required=True, default = 'draft'),


