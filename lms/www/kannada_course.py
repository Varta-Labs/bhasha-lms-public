from urllib.parse import quote

import frappe
from frappe.utils import fmt_money

from lms.lms.utils import get_lms_route


COURSE_TITLE = "Kannada Test Course API"
DEFAULT_PRICE = "₹10"


def get_context(context):
	context.no_cache = 1
	context.no_header = 1
	context.no_breadcrumbs = 1
	context.title = "Online Kannada Course | Bhasha.io"
	context.description = (
		"Learn Kannada online with live coaching, structured lessons, speaking practice, "
		"and a practical course path built for busy learners."
	)

	course = get_course()
	course_name = course.name if course else None
	billing_url = get_lms_route(f"billing/course/{course_name}") if course_name else "#"
	login_url = f"/login?redirect-to={quote(billing_url)}"
	signup_url = f"{login_url}#signup"
	course_url = get_lms_route(f"courses/{course_name}") if course_name else "#"
	is_logged_in = frappe.session.user != "Guest"
	is_paid_course = bool(course and course.paid_course and course.course_price and course.currency)
	is_enrolled = (
		is_logged_in
		and course
		and frappe.db.exists(
			"LMS Enrollment",
			{"member": frappe.session.user, "course": course.name},
		)
	)

	context.course = course or frappe._dict()
	context.course_name = course_name
	context.course_url = course_url
	context.billing_url = billing_url
	context.login_url = login_url
	context.signup_url = signup_url
	context.cta_url = get_cta_url(is_enrolled, is_logged_in, is_paid_course, course_url, billing_url, signup_url)
	context.cta_label = get_cta_label(is_enrolled, is_logged_in, is_paid_course)
	context.price = get_price(course)
	context.original_price = "₹8,999"
	context.meta_image = get_meta_image(course)
	return context


def get_course():
	if frappe.form_dict.get("course") and is_paid_course(frappe.form_dict.course):
		return get_course_doc(frappe.form_dict.course)

	course_name = frappe.db.exists(
		"LMS Course",
		{"title": COURSE_TITLE, "published": 1, "paid_course": 1},
	)
	if course_name:
		return get_course_doc(course_name)

	course_name = frappe.db.get_value(
		"LMS Course",
		{"category": "Kannada", "published": 1, "paid_course": 1},
		"name",
		order_by="modified desc",
	)
	if course_name:
		return get_course_doc(course_name)

	course_name = frappe.db.sql(
		"""
		select name
		from `tabLMS Course`
		where published = 1
			and paid_course = 1
			and (title like %(term)s or tags like %(term)s or category = %(category)s)
		order by modified desc
		limit 1
		""",
		{"term": "%Kannada%", "category": "Kannada"},
		as_dict=True,
	)
	if course_name:
		return get_course_doc(course_name[0].name)

	return None


def get_course_doc(course_name):
	return frappe.db.get_value(
		"LMS Course",
		course_name,
		[
			"name",
			"title",
			"short_introduction",
			"image",
			"course_price",
			"currency",
			"paid_course",
			"enrollments",
			"rating",
			"lessons",
		],
		as_dict=True,
	)


def is_paid_course(course_name):
	return frappe.db.exists(
		"LMS Course",
		{"name": course_name, "published": 1, "paid_course": 1},
	)


def get_cta_url(is_enrolled, is_logged_in, is_paid_course, course_url, billing_url, signup_url):
	if is_enrolled:
		return course_url
	if not is_paid_course:
		return "#"
	return billing_url if is_logged_in else signup_url


def get_cta_label(is_enrolled, is_logged_in, is_paid_course):
	if is_enrolled:
		return "Go to course"
	if not is_paid_course:
		return "Course unavailable"
	return "Sign up and Enroll"


def get_price(course):
	if course and course.paid_course and course.course_price:
		return fmt_money(course.course_price, 0, course.currency or "INR")
	return DEFAULT_PRICE


def get_meta_image(course):
	if course and course.image:
		return course.image
	return "/assets/lms/images/kannada-course-hero-800.webp"
