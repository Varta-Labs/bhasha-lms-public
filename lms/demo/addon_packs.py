"""Seed the real Addons Pack packages on the disposable local verification site."""

import frappe

from lms.course_importer import import_addon_courses, import_course


def create_local_catalog():
	if frappe.local.site != "lms.localhost" or not frappe.conf.developer_mode:
		frappe.throw("This seed is restricted to the local development site.")
	frappe.set_user("Administrator")
	frappe.db.set_single_value("LMS Settings", {"allow_guest_access": 1, "disable_pwa": 1, "apply_gst": 0})
	languages = ("kannada", "hindi", "tamil", "telugu", "malayalam", "marathi")
	for language in languages:
		import_course(f"{language}-for-everyday-conversations.json", publish=1, validate_remote=0)
	packs = import_addon_courses(publish=1, validate_remote=0)
	for email, first_name in (("addons.learner@example.com", "Addons Learner"), ("addons.unpurchased@example.com", "Addons Visitor")):
		if not frappe.db.exists("User", email):
			frappe.get_doc({"doctype": "User", "email": email, "first_name": first_name, "user_type": "Website User", "send_welcome_email": 0, "roles": [{"role": "LMS Student"}], "new_password": "AddonsLocalOnly-2026!"}).insert(ignore_permissions=True)
	for language in languages:
		for course in (f"{language}-addons", f"{language}-for-everyday-conversations"):
			if not frappe.db.exists("LMS Enrollment", {"member": "addons.learner@example.com", "course": course}):
				frappe.get_doc({"doctype": "LMS Enrollment", "member": "addons.learner@example.com", "course": course}).insert(ignore_permissions=True)
	frappe.db.commit()
	return [{"course": pack["course"], "chapters": len(pack["chapters"]), "lessons": len(pack["lessons"])} for pack in packs]
