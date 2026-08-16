from urllib.parse import parse_qs, quote, urlparse

import frappe
from frappe import _

from lms.lms.api import verify_billing_access

from lms.lms.utils import (
	complete_enrollment,
	get_lms_route,
	get_order_summary,
)


def get_payment_gateway():
	return frappe.db.get_single_value("LMS Settings", "payment_gateway")


def get_controller(payment_gateway):
	if "payments" in frappe.get_installed_apps():
		from payments.utils import get_payment_gateway_controller

		return get_payment_gateway_controller(payment_gateway)


def validate_currency(payment_gateway, currency):
	controller = get_controller(payment_gateway)
	controller().validate_transaction_currency(currency)


@frappe.whitelist()
def get_payment_link(
	doctype: str,
	docname: str,
	address: dict,
	payment_for_certificate: int,
	coupon_code: str | None = None,
	country: str | None = None,
):
	validate_payment_access(doctype, docname, payment_for_certificate)
	payment_gateway = get_payment_gateway()
	address = frappe._dict(address)
	redirect_to = get_redirect_url(doctype, docname, payment_for_certificate)

	details = frappe._dict(get_order_summary(doctype, docname, coupon=coupon_code, country=country))
	title = details.title
	currency = details.currency
	original_amount = details.original_amount
	discount_amount = details.get("discount_amount", 0)
	gst_amount = details.get("gst_applied", 0)
	amount = original_amount - discount_amount
	amount_with_gst = get_amount_with_gst(amount, gst_amount)
	coupon = details.get("coupon")
	total_amount = amount_with_gst if amount_with_gst else amount

	payment = record_payment(
		address,
		doctype,
		docname,
		amount,
		original_amount,
		currency,
		amount_with_gst,
		discount_amount,
		payment_for_certificate,
		coupon_code,
		coupon,
	)

	if total_amount <= 0:
		frappe.db.set_value("LMS Payment", payment.name, "payment_received", 1)
		complete_enrollment(payment.name, doctype, docname)
		return redirect_to

	controller = get_controller(payment_gateway)

	payment_details = {
		"amount": total_amount,
		"title": f"Payment for {doctype} {title} {docname}",
		"description": f"{address.billing_name}'s payment for {title}",
		"reference_doctype": doctype,
		"reference_docname": docname,
		"payer_email": frappe.session.user,
		"payer_name": address.billing_name,
		"currency": currency,
		"payment_gateway": payment_gateway,
		"redirect_to": redirect_to,
		"payment": payment.name,
	}

	create_order(payment_gateway, payment_details, controller)
	url = controller.get_payment_url(**payment_details)

	if payment_gateway == "Razorpay":
		return get_razorpay_checkout_url(url)

	return url


def validate_payment_access(doctype: str, docname: str, payment_for_certificate: int):
	billing_type = get_billing_type(doctype, payment_for_certificate)
	access, message = verify_billing_access(doctype, docname, billing_type)
	if not access:
		frappe.throw(message)


def get_billing_type(doctype: str, payment_for_certificate: int) -> str:
	if int(payment_for_certificate):
		if doctype != "LMS Course":
			frappe.throw(_("Certificates can only be purchased for courses."))
		return "certificate"
	if doctype == "LMS Course":
		return "course"
	if doctype == "LMS Batch":
		return "batch"
	frappe.throw(_("Invalid payment document type."))


def create_order(payment_gateway: str, payment_details: dict, controller: object):
	if payment_gateway != "Razorpay":
		return

	order = controller.create_order(**payment_details)
	order_id = order.get("id") if order else None
	if not order_id:
		frappe.throw(
			_(
				"Unable to create a Razorpay order. Please verify the Razorpay API Key and API Secret in Razorpay Settings."
			)
		)

	payment_details.update({"order_id": order_id})


def get_razorpay_checkout_url(payment_url: str) -> str:
	"""Use the LMS checkout wrapper so dismissed payments return to billing."""
	token = parse_qs(urlparse(payment_url).query).get("token", [None])[0]
	if not token:
		return payment_url
	return f"/lms_razorpay_checkout?token={quote(token)}"


def get_amount_with_gst(amount: float, gst_amount: float) -> float:
	amount_with_gst = 0
	if gst_amount:
		amount_with_gst = amount + gst_amount

	return amount_with_gst


def record_payment(
	address: dict,
	doctype: str,
	docname: str,
	amount: float,
	original_amount: float,
	currency: str,
	amount_with_gst: float = 0,
	discount_amount: float = 0,
	payment_for_certificate: int = 0,
	coupon_code: str | None = None,
	coupon: str | None = None,
):
	address = frappe._dict(address)
	address_name = save_address(address)

	payment_doc = frappe.new_doc("LMS Payment")
	payment_doc.update(
		{
			"member": frappe.session.user,
			"billing_name": address.billing_name,
			"address": address_name,
			"amount": amount,
			"currency": currency,
			"discount_amount": discount_amount,
			"amount_with_gst": amount_with_gst,
			"gstin": address.get("gstin", ""),
			"pan": address.get("pan", ""),
			"source": address.get("source") or get_checkout_source(),
			"payment_for_document_type": doctype,
			"payment_for_document": docname,
			"payment_for_certificate": payment_for_certificate,
			"member_consent": address.get("member_consent", 0),
		}
	)
	if coupon_code:
		payment_doc.update(
			{
				"coupon": coupon,
				"coupon_code": coupon_code,
				"discount_amount": discount_amount,
				"original_amount": original_amount,
			}
		)

	payment_doc.save(ignore_permissions=True)
	return payment_doc


def get_checkout_source() -> str:
	"""Return a source for legacy installations where it is still mandatory."""
	source = frappe.db.get_value("LMS Source", {"source": "Website"}, "name")
	if source:
		return source

	source = frappe.db.get_value("LMS Source", {}, "name", order_by="creation asc")
	if source:
		return source

	source_doc = frappe.get_doc({"doctype": "LMS Source", "source": "Website"})
	source_doc.insert(ignore_permissions=True)
	return source_doc.name


def get_redirect_url(doctype: str, docname: str, payment_for_certificate: int) -> str:
	if int(payment_for_certificate):
		return get_lms_route(f"payment-success/certificate/{docname}")
	elif doctype == "LMS Course":
		return get_lms_route(f"payment-success/course/{docname}")
	else:
		return get_lms_route(f"payment-success/batch/{docname}")


def save_address(address: dict) -> str:
	# The checkout only collects the address details needed for course enrollment.
	# Frappe still requires an address line, so use the learner's city when no
	# street address has been provided.
	address.address_line1 = address.get("address_line1") or address.get("city")
	filters = {"email_id": frappe.session.user}
	exists = frappe.db.exists("Address", filters)
	if exists:
		address_doc = frappe.get_last_doc("Address", filters=filters)
	else:
		address_doc = frappe.new_doc("Address")

	address_doc.update(address)
	address_doc.update(
		{
			"address_title": address.billing_name,
			"address_type": "Billing",
			"is_primary_address": 1,
			"email_id": frappe.session.user,
		}
	)
	address_doc.save(ignore_permissions=True)
	return address_doc.name
