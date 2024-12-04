# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2019- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
#from bs4 import BeautifulSoup
import odoo.tools
import re
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ScrumSprintPortfolio(models.Model):
    _name = 'project.scrum.portfolio'
    _inherit = ['mail.thread']
    _description = 'Project Scrum Portfolio'
    _order = 'name desc'

    name = fields.Char(string='Portfolio Name', required=True, help='Product or focus area')
    description = fields.Text(string='Description', required=False)
    color = fields.Integer(string='Color Index')
    timebox_ids = fields.One2many(comodel_name="project.scrum.timebox", inverse_name='portfolio_id')

    @api.depends('timebox_ids')
    def _timebox_count(self):
        for rec in self:
            if rec.timebox_ids:
                rec.timebox_count = len(rec.timebox_ids)
            else:
                rec.timebox_count = 0

    timebox_count = fields.Integer(compute='_timebox_count')
    user_id = fields.Many2one(comodel_name='res.users', string='Product Owner',
                              help="Manager for a product or Focus Area")

    @api.depends('timebox_ids')
    def _planned_hours(self):
        for rec in self:
            if rec.timebox_ids:
                rec.planned_hours = sum(rec.timebox_ids.filtered(
                    lambda tb: tb.sprint_id and tb.state in ['draft', '']).mapped('planned_hours'))
                rec.consumed_hours = sum(rec.timebox_ids.filtered(
                    lambda tb: tb.sprint_id and tb.state in ['done']).mapped('planned_hours'))
            else:
                rec.planned_hours = 0
                rec.consumed_hours = 0

            if rec.env.context.get('sprint_ids'):
                rec.sprint_hours = sum(rec.timebox_ids.filtered(
                    lambda tb: tb.sprint_id.id in tb.env.context.get('sprint_ids')).mapped('planned_hours'))
            else:
                rec.sprint_hours = sum(rec.timebox_ids.mapped('planned_hours')) if rec.timebox_ids else 0.0

    planned_hours = fields.Float(compute="_planned_hours", aggregator="sum", string='Planned Hours',
                                 help="Hours timeboxed for sprints planned", readonly=True)
    consumed_hours = fields.Float(compute="_planned_hours", aggregator="sum", string='Consumed Hours',
                                  help="Hours consumed for done sprints", readonly=True)
    sprint_hours = fields.Float(compute="_planned_hours", aggregator="sum", string='Sprint Hours',
                                help="Hours timeboxed for current sprints", readonly=True)


class ScrumSprintTimebox(models.Model):
    _name = 'project.scrum.timebox'
    _description = 'Project Scrum Timebox'

    portfolio_id = fields.Many2one(comodel_name='project.scrum.portfolio')
    sprint_id = fields.Many2one(comodel_name="project.scrum.sprint")
    planned_hours = fields.Float(string="Planned Hours")

    @api.depends('sprint_id')
    def _state(self):
        for rec in self:
            if rec.sprint_id:
                rec.state = rec.sprint_id.state
            else:
                rec.state = False

    state = fields.Char(string="State", compute="_state")

    @api.depends('planned_hours', 'sprint_id')
    def _sprint_share(self):
        for rec in self:
            if rec.planned_hours:
                rec.sprint_share = round(
                    rec.planned_hours / (
                        rec.sprint_id.planned_hours if rec.sprint_id and rec.sprint_id.planned_hours else
                        1.0) * 100.0)
            else:
                rec.sprint_share = 0

    sprint_share = fields.Float(compute="_sprint_share", readonly=True)


class ScrumSprint(models.Model):
    _inherit = 'project.scrum.sprint'

    timebox_ids = fields.One2many(comodel_name="project.scrum.timebox", inverse_name='sprint_id')


class ProjectTask(models.Model):
    _inherit = "project.task"

    color = fields.Integer(string='Color Index', related='portfolio_id.color')
    portfolio_id = fields.Many2one(comodel_name="project.scrum.portfolio")

