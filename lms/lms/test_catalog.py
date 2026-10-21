from contextlib import ExitStack
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from lms.lms.utils import get_courses


class TestCatalog(FrappeTestCase):
	def test_featured_addons_follow_main_courses_and_database_orders_before_pagination(self):
		main = frappe._dict(name="main", addon_for_course=None)
		other_main = frappe._dict(name="other-main", addon_for_course="")
		pack = frappe._dict(name="pack", addon_for_course="main")
		featured_pack = frappe._dict(name="featured-pack", addon_for_course="other-main")
		with ExitStack() as stack:
			stack.enter_context(patch("lms.lms.utils.guest_access_allowed", return_value=True))
			stack.enter_context(patch("lms.lms.utils.update_course_filters", return_value=({}, {}, True)))
			stack.enter_context(patch("lms.lms.utils.get_course_fields", return_value=["name", "addon_for_course"]))
			query = stack.enter_context(patch("lms.lms.utils.frappe.get_all", return_value=[main, other_main, pack]))
			stack.enter_context(patch("lms.lms.utils.get_featured_courses", return_value=[featured_pack]))
			stack.enter_context(patch("lms.lms.utils.get_enrollment_details", side_effect=lambda courses: courses))
			stack.enter_context(patch("lms.lms.utils.get_course_card_details", side_effect=lambda courses: courses))
			self.assertEqual([course.name for course in get_courses()], ["main", "other-main", "featured-pack", "pack"])
		self.assertEqual(query.call_args.kwargs["order_by"], "addon_for_course asc, enrollments desc, title asc")
