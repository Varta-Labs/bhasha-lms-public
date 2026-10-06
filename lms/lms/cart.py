"""Course cart pricing and payment fulfillment. The browser sends course IDs only."""

import hashlib
import hmac
from decimal import Decimal, ROUND_HALF_UP

import frappe
from frappe import _
from frappe.utils import cint, flt, fmt_money

from lms.lms.utils import (
	apply_coupon,
	apply_gst,
	check_multicurrency,
	get_lms_route,
)


def money(value):
	try:
		amount = Decimal(str(value or 0))
		if not amount.is_finite():
			raise ValueError
		return float(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
	except (ValueError, ArithmeticError):
		frappe.throw(_("Invalid order amount."))


def course_names(courses):
	if isinstance(courses, str):
		courses = frappe.parse_json(courses)
	if not isinstance(courses, list) or len(courses) > 20 or any(not isinstance(c, str) for c in courses):
		frappe.throw(_("Please select up to 20 courses."))
	return list(dict.fromkeys(courses))


def owns(course, member=None):
	member = member or frappe.session.user
	return member != "Guest" and bool(frappe.db.exists("LMS Enrollment", {"member": member, "course": course}))


def saleable(course):
	return bool(course.published and not course.upcoming and course.paid_course and not course.disable_self_learning)


def priced_item(course, country, selected):
	amount, currency = check_multicurrency(course.course_price, course.currency, country, course.amount_usd)
	amount = money(amount)
	if amount < 0 or not currency:
		frappe.throw(_("This course has invalid pricing."))
	eligible = course.addon_for_course and (course.addon_for_course in selected or owns(course.addon_for_course))
	discount = money(amount * flt(course.bundle_discount_percent) / 100) if eligible else 0
	return frappe._dict(
		course=course.name, title=course.title, image=course.image,
		short_introduction=course.short_introduction, currency=currency,
		original_amount=amount, discount_amount=discount, amount=money(amount - discount),
		bundle_discount_percent=course.bundle_discount_percent,
	)


@frappe.whitelist(allow_guest=True)
def get_cart_summary(courses, country=None, coupon_code=None):
	names = course_names(courses)
	items, owned, unavailable = [], [], []
	for name in names:
		if not frappe.db.exists("LMS Course", name):
			unavailable.append({"course": name, "title": name})
			continue
		course = frappe.get_doc("LMS Course", name)
		if owns(name):
			owned.append({"course": name, "title": course.title})
		elif not saleable(course):
			# Do not expose unpublished course details to a guest.
			unavailable.append({"course": name, "title": course.title if course.published else name})
		else:
			items.append(priced_item(course, country, names))
	if len({item.currency for item in items}) > 1:
		frappe.throw(_("Please purchase courses with different currencies separately."))
	currency = items[0].currency if items else "INR"
	original = money(sum(i.original_amount for i in items))
	bundle_discount = money(sum(i.discount_amount for i in items))
	coupon_name = None
	discount_label = _("Bundle savings") if bundle_discount else ""
	if coupon_code and items:
		# A coupon is evaluated once against its eligible items, then compared
		# with the bundle saving. The existing Fixed Amount coupon sets a final
		# eligible subtotal; its saving is never multiplied per course.
		eligible = [i for i in items if frappe.db.exists("LMS Coupon Item", {
			"parent": frappe.db.get_value("LMS Coupon", {"code": coupon_code, "enabled": 1}, "name"),
			"reference_doctype": "LMS Course", "reference_name": i.course,
		})]
		if not eligible:
			frappe.throw(_("This coupon does not apply to the courses in your cart."))
		base = money(sum(i.original_amount for i in eligible))
		discount, coupon_subtotal, candidate = apply_coupon("LMS Course", eligible[0].course, coupon_code, base)
		discount = money(min(discount, base))
		if discount > bundle_discount:
			coupon_name = candidate
			discount_label = _("Coupon savings")
			remaining = discount
			for item in items:
				item.discount_amount = 0
			for index, item in enumerate(eligible):
				item.discount_amount = remaining if index == len(eligible) - 1 else min(remaining, money(discount * item.original_amount / base))
				remaining = money(remaining - item.discount_amount)
			for item in items:
				item.amount = money(item.original_amount - item.discount_amount)
		discount_label = discount_label or _("Coupon savings")
	discount = money(sum(i.discount_amount for i in items))
	subtotal = money(original - discount)
	total, gst = apply_gst(subtotal, country) if currency == "INR" else (subtotal, 0)
	for item in items:
		item.original_amount_formatted = fmt_money(item.original_amount, 2, currency)
		item.amount_formatted = fmt_money(item.amount, 2, currency)
		item.discount_amount_formatted = fmt_money(item.discount_amount, 2, currency)
	suggestions = []
	if names:
		for course in frappe.get_all("LMS Course", filters={"addon_for_course": ["in", names], "published": 1}, pluck="name"):
			if course in names or owns(course):
				continue
			doc = frappe.get_doc("LMS Course", course)
			if saleable(doc):
				item = priced_item(doc, country, names)
				if not items or item.currency == currency:
					item.amount_formatted = fmt_money(item.amount, 2, item.currency)
					item.discount_amount_formatted = fmt_money(item.discount_amount, 2, item.currency)
					suggestions.append(item)
	return frappe._dict(
		title=_("Your courses"), items=items, suggestions=suggestions,
		owned_courses=owned, unavailable_courses=unavailable, currency=currency,
		original_amount=original, discount_amount=discount, subtotal=subtotal,
		gst_applied=money(gst), total_amount=money(total), discount_label=discount_label,
		coupon=coupon_name, coupon_code=coupon_code if coupon_name else None,
		original_amount_formatted=fmt_money(original, 2, currency),
		discount_amount_formatted=fmt_money(discount, 2, currency),
		gst_amount_formatted=fmt_money(gst, 2, currency),
		total_amount_formatted=fmt_money(total, 2, currency),
	)


@frappe.whitelist()
def get_checkout_access():
	if frappe.session.user == "Guest":
		frappe.throw(_("Please sign in to checkout."), frappe.PermissionError)
	address = frappe.db.get_value("Address", {"email_id": frappe.session.user},
		["address_title as billing_name", "phone", "city", "country"], as_dict=True)
	return {"access": True, "address": address}


@frappe.whitelist()
def get_cart_payment_link(courses, address, expected_total, expected_currency, coupon_code=None):
	from lms.lms.payments import (
		create_order, get_controller, get_payment_gateway, get_razorpay_checkout_url, record_payment,
	)
	get_checkout_access()
	address = frappe._dict(frappe.parse_json(address) if isinstance(address, str) else address)
	for field in ("billing_name", "phone", "city", "country"):
		if not address.get(field) or not isinstance(address[field], str) or not address[field].strip():
			frappe.throw(_("Please complete your billing details."))
	# Country used for pricing and tax is always the billing country.
	details = get_cart_summary(courses, address.country, coupon_code)
	if details.unavailable_courses:
		frappe.throw(_("Remove unavailable courses before checking out."))
	if not details["items"]:
		frappe.throw(_("Your cart has no courses to purchase."))
	if money(expected_total) != details.total_amount or expected_currency != details.currency:
		frappe.throw(_("Your order total has changed. Please review the updated total before paying."))
	order = frappe.get_doc({
		"doctype": "LMS Course Order", "member": frappe.session.user, "status": "Pending",
		"currency": details.currency, "country": address.country,
		"original_amount": details.original_amount, "discount_amount": details.discount_amount,
		"subtotal": details.subtotal, "gst_amount": details.gst_applied,
		"total_amount": details.total_amount, "discount_label": details.discount_label,
		"coupon": details.coupon, "coupon_code": details.coupon_code,
		"items": [{key: item[key] for key in ("course", "title", "original_amount", "discount_amount", "amount")} for item in details["items"]],
	}).insert(ignore_permissions=True)
	payment = record_payment(
		address, "LMS Course Order", order.name, details.subtotal, details.original_amount,
		details.currency, details.total_amount if details.gst_applied else 0,
		details.discount_amount, 0, details.coupon_code, details.coupon,
	)
	frappe.db.set_value("LMS Payment", payment.name, "original_amount", details.original_amount)
	frappe.db.set_value("LMS Course Order", order.name, "payment", payment.name)
	redirect = get_lms_route(f"payment-success/order/{order.name}")
	if details.total_amount <= 0:
		fulfill_order(order.name, payment.name)
		return redirect
	gateway = get_payment_gateway()
	controller = get_controller(gateway)
	if not controller:
		frappe.throw(_("The payment gateway is not configured."))
	kwargs = dict(
		amount=details.total_amount, currency=details.currency,
		title=_("Bhasha course order"), description=", ".join(i.title for i in details["items"]),
		reference_doctype="LMS Course Order", reference_docname=order.name,
		payer_email=frappe.session.user, payer_name=address.billing_name,
		payment_gateway=gateway, redirect_to=redirect, payment=payment.name,
	)
	create_order(gateway, kwargs, controller)
	if kwargs.get("order_id"):
		frappe.db.set_value("LMS Payment", payment.name, "order_id", kwargs["order_id"])
	url = controller.get_payment_url(**kwargs)
	return get_razorpay_checkout_url(url) if gateway == "Razorpay" else url


def has_course_order_payment(payment, member, course):
	if not payment:
		return False
	paid = frappe.db.get_value("LMS Payment", payment, ["member", "payment_received", "payment_for_document_type", "payment_for_document"], as_dict=True)
	if not paid or paid.member != member or not paid.payment_received or paid.payment_for_document_type != "LMS Course Order":
		return False
	return bool(frappe.db.exists("LMS Course Order", {"name": paid.payment_for_document, "member": member, "payment": payment, "status": "Paid"}) and frappe.db.exists("LMS Course Order Item", {"parent": paid.payment_for_document, "parenttype": "LMS Course Order", "course": course}))


def fulfill_order(order_name, payment_name, payment_id=None):
	# Serialize callbacks/webhooks and roll back payment + all enrollments together.
	order = frappe.get_doc("LMS Course Order", order_name, for_update=True)
	payment = frappe.get_doc("LMS Payment", payment_name)
	if order.payment != payment.name or payment.member != order.member or payment.payment_for_document_type != "LMS Course Order" or payment.payment_for_document != order.name:
		frappe.throw(_("Payment does not belong to this order."))
	if order.status == "Paid":
		return
	if not payment_id and order.total_amount > 0:
		frappe.throw(_("Payment has not been confirmed."))
	frappe.db.savepoint("course_order_fulfillment")
	try:
		frappe.db.set_value("LMS Payment", payment.name, {"payment_received": 1, "payment_id": payment_id})
		frappe.db.set_value("LMS Course Order", order.name, "status", "Paid")
		for item in order.items:
			if not owns(item.course, order.member):
				frappe.get_doc({"doctype": "LMS Enrollment", "member": order.member, "course": item.course, "payment": payment.name}).insert(ignore_permissions=True)
		if order.coupon:
			frappe.db.sql("UPDATE `tabLMS Coupon` SET redemption_count = COALESCE(redemption_count, 0) + 1 WHERE name = %s", order.coupon)
	except Exception:
		frappe.db.rollback(save_point="course_order_fulfillment")
		raise


def confirm_order_payment(order_name):
	"""Called only by the payment gateway's authorized-payment document hook."""
	order = frappe.get_doc("LMS Course Order", order_name)
	data = getattr(frappe.flags, "data", None) or {}
	payment_name = data.get("payment")
	requests = frappe.get_all("Integration Request", filters={"reference_doctype": "LMS Course Order", "reference_docname": order.name}, fields=["data"], order_by="creation desc", limit=20)
	for request in requests:
		details = frappe._dict(frappe.parse_json(request.data))
		if details.payment != order.payment or (payment_name and details.payment != payment_name):
			continue
		from lms.lms.utils import get_payment_id
		payment_id = details.get(get_payment_id(details))
		if not payment_id:
			frappe.throw(_("Payment has not been confirmed."))
		if details.payment_gateway == "Razorpay":
			payment = frappe.get_doc("LMS Payment", order.payment)
			entity = fetch_razorpay_payment(payment_id)
			if not validate_razorpay_payment(order, payment, entity):
				return
		fulfill_order(order.name, details.payment, payment_id)
		return
	frappe.throw(_("No matching payment confirmation was found."))


def fetch_razorpay_payment(payment_id):
	from frappe.integrations.utils import make_get_request
	settings = frappe.get_doc("Razorpay Settings").get_settings({})
	return make_get_request(
		f"https://api.razorpay.com/v1/payments/{payment_id}",
		auth=(settings.api_key, settings.api_secret),
	)


def validate_razorpay_payment(order, payment, entity):
	if not payment.order_id or entity.get("order_id") != payment.order_id or entity.get("currency") != order.currency or cint(entity.get("amount")) != cint(Decimal(str(order.total_amount)) * 100):
		frappe.throw(_("Payment amount, currency or gateway order does not match this order."))
	return entity.get("status") == "captured"


@frappe.whitelist()
def get_order_status(order_name):
	order = frappe.get_doc("LMS Course Order", order_name)
	if order.member != frappe.session.user:
		frappe.throw(_("This order belongs to another learner."), frappe.PermissionError)
	return {"status": order.status, "courses": [{"course": i.course, "title": i.title, "enrolled": owns(i.course)} for i in order.items]}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def razorpay_webhook():
	"""Captured-payment fallback when checkout is closed before its callback."""
	secret = frappe.conf.get("bhasha_razorpay_webhook_secret")
	if not secret:
		frappe.throw(_("Payment webhook is not configured."), frappe.PermissionError)
	body = frappe.request.get_data()
	signature = frappe.request.headers.get("X-Razorpay-Signature", "")
	expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
	if not hmac.compare_digest(signature, expected):
		frappe.throw(_("Invalid payment signature."), frappe.PermissionError)
	event = frappe.parse_json(body.decode("utf-8"))
	if event.get("event") != "payment.captured":
		return {"received": True}
	entity = event["payload"]["payment"]["entity"]
	payment_name = frappe.db.get_value("LMS Payment", {"order_id": entity.get("order_id"), "payment_for_document_type": "LMS Course Order"}, "name") if entity.get("order_id") else None
	if not payment_name:
		return {"received": True}
	payment = frappe.get_doc("LMS Payment", payment_name)
	order = frappe.get_doc("LMS Course Order", payment.payment_for_document)
	if not entity.get("id") or not validate_razorpay_payment(order, payment, entity):
		frappe.throw(_("Payment has not been captured."))
	fulfill_order(order.name, payment.name, entity["id"])
	return {"received": True}
