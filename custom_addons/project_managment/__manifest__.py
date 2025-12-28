# -*- coding: utf-8 -*-
{
    "name": "Project Management",
    "summary": "Project Management System for AI Research Centre HSE University",
    "category": "Project",
    "version": "19.0.0.1.0",
    "author": "Dandamaev Gadji",
    "license": "LGPL-3",
    "depends": [
                "base",
                "project", 
                "mail", 
    ],
    "data": [
        # Security
        "security/security.xml",
        "security/ir.model.access.csv",

        # Views
        "views/project_views.xml",
    ],
    "application": True,
    "installable": True,
}
