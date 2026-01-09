# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    _logger.info(">>> project.project EXTENDED (member_ids added) <<<")


    # Паспорт (минимум для MVP)
    name_en = fields.Char(string="Название проекта (EN)")

    project_status = fields.Selection(
        [
            ("draft", "Черновик"),
            ("in_progress", "В работе"),
            ("done", "Завершено"),
            ("archive", "Архив"),
        ],
        string="Статус проекта",
        default="draft",
        tracking=True,
    )

    project_type = fields.Selection(
        [
            ("research", "Исследование (R&D)"),
            ("contract", "Контракт / Промышленность"),
            ("education", "Образовательный"),
            ("infrastructure", "Инфраструктура"),
            ("other", "Другое"),
        ],
        string="Тип проекта",
        default="research",
        tracking=True,
    )

    department_name = fields.Char(string="Название отдела / подразделения")
    project_owner_id = fields.Many2one(
        "res.users",
        string="Владелец проекта",
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )

    date_start = fields.Date(string="Дата начала")
    date_end = fields.Date(string="Дата окончания")

    # Ссылки (минимальный набор)
    link_repo = fields.Char(string="URL репозитория")
    link_docs = fields.Char(string="URL документации / Drive")
    link_design = fields.Char(string="URL дизайна")
    link_chat = fields.Char(string="URL чата / канала")
    link_meeting = fields.Char(string="URL встречи")

    # Дополнительные ссылки
    link_ids = fields.One2many(
        "university.project.link",
        "project_id",
        string="Дополнительные ссылки",
        copy=True,
    )

    # Команда
    member_ids = fields.One2many(
        "university.project.member",
        "project_id",
        string="Команда проекта",
        copy=True,
    )

    member_user_ids = fields.Many2many(
        "res.users",
        compute="_compute_member_user_ids",
        string="Пользователи команды",
        store=False,
    )

    #Вложения
    document_ids = fields.One2many(
        "university.project.document",
        "project_id",
        string="Документы проекта",
        copy=True,
    )

    @api.depends("member_ids.user_id")
    def _compute_member_user_ids(self):
        for project in self:
            project.member_user_ids = project.member_ids.mapped("user_id")

    @api.onchange('member_ids')
    def _onchange_member_ids(self):
        manager_member = self.member_ids.filtered(lambda m: m.role_id.code == "project_manager")
        if manager_member:
            self.user_id = manager_member[0].user_id
        else:
            self.user_id = False

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

