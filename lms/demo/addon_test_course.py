"""A small local-only catalog for verifying the cart with a practice pack."""

import json

import frappe


def create_dummy_addon_courses():
	if frappe.local.site != "lms.localhost" or not frappe.conf.developer_mode:
		frappe.throw("Dummy cart courses can only be created on the local development site.")
	frappe.set_user("Administrator")
	category = "Kannada"
	if not frappe.db.exists("LMS Category", category):
		frappe.get_doc({"doctype": "LMS Category", "category": category}).insert(ignore_permissions=True)

	def course(name, title, price, main=None):
		existing = frappe.db.get_value("LMS Course", {"title": title}, "name")
		if existing:
			return frappe.get_doc("LMS Course", existing)
		return frappe.get_doc({
			"doctype": "LMS Course", "name": name, "title": title,
			"short_introduction": "Local dummy content for cart and enrollment verification.",
			"description": "This course contains dummy content for testing. It is not a live product.",
			"category": category, "published": 1, "paid_course": 1,
			"course_price": price, "currency": "INR", "disable_self_learning": 0,
			"addon_for_course": main, "bundle_discount_percent": 20 if main else 0,
			"instructors": [{"instructor": "Administrator"}],
		}).insert(ignore_permissions=True)

	main = course("local-demo-kannada-video", "Kannada Video Course (Local Demo)", 2000)
	pack = course("local-demo-kannada-practice-pack", "Kannada Practice Pack (Local Demo)", 500, main.name)
	for target, chapters in (
		(main, [("Getting started", "Welcome to the dummy video course.")]),
		(pack, [
			("Everyday phrases", "Namaskara — hello. Dhanyavadagalu — thank you."),
			("Tense practice", "Dummy tense exercise: write a sentence about yesterday, today and tomorrow."),
			("Workbook", "Dummy workbook exercise: practice a greeting, an introduction and a short conversation."),
		]),
	):
		for title, text in chapters:
			if frappe.db.exists("Course Chapter", {"course": target.name, "title": title}):
				continue
			chapter = frappe.get_doc({"doctype": "Course Chapter", "course": target.name, "title": title}).insert(ignore_permissions=True)
			lesson = frappe.get_doc({
				"doctype": "Course Lesson", "course": target.name, "chapter": chapter.name,
				"title": title, "content": json.dumps({"blocks": [{"type": "markdown", "data": {"text": text}}], "version": "2.29.0"}),
			}).insert(ignore_permissions=True)
			chapter.append("lessons", {"lesson": lesson.name})
			chapter.save(ignore_permissions=True)
			target.reload()
			target.append("chapters", {"chapter": chapter.name})
			target.save(ignore_permissions=True)
		from lms.lms.utils import get_lesson_count
		frappe.db.set_value("LMS Course", target.name, "lessons", get_lesson_count(target.name))
	frappe.db.set_single_value("LMS Settings", {"allow_guest_access": 1, "show_usd_equivalent": 0, "apply_gst": 0})
	member = "cart.demo@example.com"
	if not frappe.db.exists("User", member):
		frappe.get_doc({"doctype": "User", "email": member, "first_name": "Cart", "last_name": "Demo", "user_type": "Website User", "send_welcome_email": 0, "roles": [{"role": "LMS Student"}], "new_password": "CartDemoOnly-2026!"}).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"main": main.name, "pack": pack.name, "member": member, "bundle_subtotal": 2400, "pack_for_existing_owner": 400}
