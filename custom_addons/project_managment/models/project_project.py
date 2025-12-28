# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    _logger.info(">>> project.project EXTENDED (member_ids added) <<<")


    # Паспорт (минимум для MVP)
    name_en = fields.Char(string="Project name (EN)")
    short_name = fields.Char(string="Short name")

    project_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("done", "Done"),
            ("archive", "Archive"),
        ],
        string="Project status",
        default="draft",
        tracking=True,
    )

    project_type = fields.Selection(
        [
            ("research", "Research (R&D)"),
            ("contract", "Contract / Industry"),
            ("education", "Educational"),
            ("infrastructure", "Infrastructure"),
            ("other", "Other"),
        ],
        string="Project type",
        default="research",
        tracking=True,
    )

    department_name = fields.Char(string="Department / unit")
    project_owner_id = fields.Many2one(
        "res.users",
        string="Project owner",
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )

    date_start = fields.Date(string="Start date")
    date_end = fields.Date(string="End date")

    # Ссылки (минимальный набор)
    link_repo = fields.Char(string="Repository URL")
    link_docs = fields.Char(string="Docs / Drive URL")
    link_design = fields.Char(string="Design URL")
    link_chat = fields.Char(string="Chat / Channel URL")
    link_meeting = fields.Char(string="Meeting URL")

    # Команда
    member_ids = fields.One2many(
        "university.project.member",
        "project_id",
        string="Project team",
        copy=True,
    )

    member_user_ids = fields.Many2many(
        "res.users",
        compute="_compute_member_user_ids",
        string="Team users",
        store=False,
    )

    @api.depends("member_ids.user_id")
    def _compute_member_user_ids(self):
        for project in self:
            project.member_user_ids = project.member_ids.mapped("user_id")

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        # Автоматически добавляем создателя в команду (MVP-логика)
        role = self.env["university.project.role"].search([("code", "=", "owner")], limit=1)
        for project in projects:
            if not project.member_ids.filtered(lambda m: m.user_id == project.create_uid):
                self.env["university.project.member"].create({
                    "project_id": project.id,
                    "user_id": project.create_uid.id,
                    "role_id": role.id if role else False,
                })
        return projects
