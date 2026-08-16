import json

import frappe
from frappe import _
from frappe.utils import flt

from lms.lms.utils import get_lms_route


def get_context(context):
	context.no_cache = 1

	try:
		from payments.templates.pages.razorpay_checkout import get_api_key
		from payments.utils.utils import validate_integration_request

		validate_integration_request(frappe.form_dict["token"])
		integration_request = frappe.get_doc("Integration Request", frappe.form_dict["token"])
		payment_details = frappe._dict(json.loads(integration_request.data))

		context.token = frappe.form_dict["token"]
		context.reference_doctype = payment_details.reference_doctype
		context.reference_docname = payment_details.reference_docname
		context.billing_url = get_billing_url(payment_details)
		context.razorpay_options = {
			"key": get_api_key(),
			"amount": int(flt(payment_details.amount) * 100),
			"currency": payment_details.currency,
			"name": payment_details.title,
			"description": payment_details.description,
			"subscription_id": payment_details.get("subscription_id") or "",
			"order_id": payment_details.order_id,
			"prefill": {
				"name": payment_details.payer_name,
				"email": payment_details.payer_email,
			},
			"notes": dict(frappe.form_dict),
		}
	except Exception:
		frappe.redirect_to_message(
			_("Invalid Token"),
			_("The payment link is invalid. Please return to billing and try again."),
			http_status_code=400,
			indicator_color="red",
		)
		frappe.local.flags.redirect_location = frappe.local.response.location
		raise frappe.Redirect


def get_billing_url(payment_details):
	billing_type = "batch" if payment_details.reference_doctype == "LMS Batch" else "course"
	return get_lms_route(f"billing/{billing_type}/{payment_details.reference_docname}")
