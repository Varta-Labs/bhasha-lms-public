"""Integration checks for paid lesson access and bundled practice material."""

import copy
import json
from pathlib import Path
from unittest import skipUnless
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from lms.course_importer import _get_or_create_chapter, _get_or_create_course, _load_course_package, _sync_curriculum
from lms.lms.utils import get_lesson
from lms.workbooks import get_lesson_workbook


@skipUnless((Path(__file__).resolve().parents[1] / "course_data/kannada-addons.json").is_file(), "Private course packages are not installed")
class TestAddonMaterials(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		self.definition = copy.deepcopy(_load_course_package("kannada-addons.json")["course"])
		self.definition["lmsCourseId"] = f"test-addon-{frappe.generate_hash(length=10).lower()}"
		self.definition["title"] = self.definition["lmsCourseId"]
		self.definition["lmsSettings"]["addonForCourse"] = None
		self.definition["lmsSettings"]["bundleDiscountPercent"] = 0
		self.definition["lmsSettings"]["introVideoUrl"] = "https://vimeo.com/1234379445"
		self.definition["modules"] = [
			{"id": "test-videos", "title": "Videos", "chapters": [self.definition["modules"][0]["chapters"][0]]},
			{"id": "test-tables", "title": "Tables", "chapters": [self.definition["modules"][2]["chapters"][0]]},
			self.definition["modules"][-1],
		]
		self.course, _ = _get_or_create_course(self.definition, publish=1)
		self.initial = _sync_curriculum(self.course, self.definition)

	def test_unowned_paid_lesson_ignores_legacy_preview_flag(self):
		frappe.db.set_value("Course Lesson", self.initial["lessons"][0], "include_in_preview", 1)
		with patch("lms.lms.utils.get_membership", return_value=None), patch("lms.lms.utils.can_modify_course", return_value=False), patch("lms.lms.utils.guest_access_allowed", return_value=True):
			for chapter in (1, 2, 3):
				result = get_lesson(self.course.name, chapter, 1)
				self.assertEqual(result["no_preview"], 1)
				self.assertNotIn("content", result)
			with self.assertRaises(frappe.PermissionError):
				get_lesson_workbook(self.course.name, 3, 1, 0)

	def test_permitted_tables_and_workbook_render_and_reimport_preserves_lessons(self):
		tables = get_lesson(self.course.name, 2, 1)
		self.assertEqual(json.loads(tables.content)["blocks"][0]["type"], "lessonMarkdown")
		workbook = get_lesson(self.course.name, 3, 1)
		block = json.loads(workbook.content)["blocks"][0]
		self.assertEqual(block["type"], "slideDeck")
		self.assertEqual(block["data"]["kind"], "workbook")
		self.assertNotIn("filename", block["data"])
		get_lesson_workbook(self.course.name, 3, 1, 0)
		self.assertTrue(frappe.local.response.filecontent.startswith(b"%PDF"))
		frappe.local.response.pop("filecontent", None)
		frappe.local.response.type = "json"
		self.assertEqual(_sync_curriculum(self.course, self.definition)["lessons"], self.initial["lessons"])
		with self.assertRaises(frappe.DoesNotExistError):
			get_lesson_workbook(self.course.name, 3, 1, -1)

	def test_enrolled_learner_access_and_obsolete_test_chapter_replacement(self):
		member = f"addon-test-{frappe.generate_hash(length=8)}@example.com"
		frappe.get_doc({"doctype": "User", "email": member, "first_name": "Addon Test", "user_type": "Website User", "send_welcome_email": 0}).insert(ignore_permissions=True)
		enrollment = frappe.get_doc({"doctype": "LMS Enrollment", "member": member, "course": self.course.name, "progress": 25, "current_lesson": self.initial["lessons"][0]}).insert(ignore_permissions=True)
		obsolete, _ = _get_or_create_chapter(self.course, {"title": "Verb Conjugation Test"})
		self.course.reload()
		self.course.append("chapters", {"chapter": obsolete.name})
		self.course.save(ignore_permissions=True)
		result = _sync_curriculum(self.course, self.definition)
		self.assertIn(obsolete.name, result["deleted_chapters"])
		self.assertFalse(frappe.db.exists("Course Chapter", obsolete.name))
		self.assertEqual(result["lessons"], self.initial["lessons"])
		enrollment.reload()
		self.assertEqual(enrollment.progress, 25)
		self.assertEqual(enrollment.current_lesson, self.initial["lessons"][0])
		try:
			frappe.set_user(member)
			self.assertIn("content", get_lesson(self.course.name, 2, 1))
			get_lesson_workbook(self.course.name, 3, 1, 0)
			self.assertTrue(frappe.local.response.filecontent.startswith(b"%PDF"))
		finally:
			frappe.set_user("Administrator")
			frappe.local.response.pop("filecontent", None)
			frappe.local.response.type = "json"
