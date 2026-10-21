"""Serve bundled practice workbooks through the lesson's normal access checks."""

import json
import re
from pathlib import Path

import frappe
from frappe import _
from frappe.utils import cint


def workbook_path(filename):
	if not isinstance(filename, str) or not re.fullmatch(r"[a-z0-9-]+\.pdf", filename):
		raise ValueError("Invalid workbook filename.")
	path = Path(frappe.get_app_path("lms")) / "course_data" / "workbooks" / filename
	if not path.is_file() or not path.read_bytes().startswith(b"%PDF"):
		raise ValueError(f"Workbook is missing or invalid: {filename}")
	return path


@frappe.whitelist(allow_guest=True)
def get_lesson_workbook(course: str, chapter: int, lesson: int, block: int):
	from lms.lms.utils import get_lesson

	details = get_lesson(course, chapter, lesson)
	if not details or details.get("no_preview"):
		frappe.throw(_("You do not have access to this lesson."), frappe.PermissionError)
	try:
		blocks = json.loads(frappe.db.get_value("Course Lesson", details.name, "content") or "{}")["blocks"]
		index = cint(block)
		if index < 0:
			raise ValueError("Invalid block")
		definition = blocks[index]
		if definition["type"] != "workbook":
			raise ValueError("Not a workbook")
		path = workbook_path(definition["data"]["filename"])
	except (KeyError, IndexError, TypeError, ValueError):
		frappe.throw(_("Workbook not found."), frappe.DoesNotExistError)
	frappe.local.response.filename = path.name
	frappe.local.response.filecontent = path.read_bytes()
	frappe.local.response.type = "download"
	frappe.local.response.content_type = "application/pdf"
	frappe.local.response.display_content_as = "inline"
