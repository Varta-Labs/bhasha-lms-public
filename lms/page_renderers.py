"""Custom page renderers for LMS app.

Handles rendering of profile pages.
"""

import mimetypes
import os

import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer
from werkzeug.wrappers import Response
from werkzeug.wsgi import wrap_file


class LMSServiceWorkerRenderer(BaseRenderer):
	"""Serve the generated worker from inside the LMS route so it can control the app."""

	endpoint = "_lms_service_worker"

	def can_render(self):
		return self.path == self.endpoint

	def render(self):
		worker_path = frappe.get_app_path("lms", "public", "frontend", "sw.js")
		if not os.path.isfile(worker_path):
			return Response(
				"Service worker has not been built.",
				status=503,
				content_type="application/javascript",
			)

		with open(worker_path, "rb") as worker_file:
			response = Response(worker_file.read(), content_type="application/javascript")

		# Always revalidate so browsers detect a newly deployed worker immediately.
		response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
		response.headers["X-Content-Type-Options"] = "nosniff"
		return response


class SCORMRenderer(BaseRenderer):
	def can_render(self):
		return "scorm/" in self.path

	def _is_safe_path(self, path):
		scorm_root = os.path.realpath(os.path.join(frappe.local.site_path, "public", "scorm"))
		resolved = os.path.realpath(path)
		return resolved.startswith(scorm_root + os.sep) or resolved == scorm_root

	def _serve_file(self, path):
		f = open(path, "rb")
		response = Response(wrap_file(frappe.local.request.environ, f), direct_passthrough=True)
		response.mimetype = mimetypes.guess_type(path)[0]
		return response

	def render(self):
		path = os.path.join(frappe.local.site_path, "public", self.path.lstrip("/"))

		if not self._is_safe_path(path):
			raise frappe.PermissionError

		extension = os.path.splitext(path)[1]
		if not extension:
			path = f"{path}.html"

		# check if path exists and is actually a file and not a folder
		if os.path.exists(path) and os.path.isfile(path):
			return self._serve_file(path)
		else:
			path = path.replace(".html", "")
			if os.path.exists(path) and os.path.isdir(path):
				index_path = os.path.join(path, "index.html")
				if os.path.exists(index_path):
					return self._serve_file(index_path)
			elif not os.path.exists(path):
				chapter_folder = "/".join(self.path.split("/")[:3])
				chapter_folder_path = os.path.realpath(frappe.get_site_path("public", chapter_folder))
				file = path.split("/")[-1]
				correct_file_path = None

				if not self._is_safe_path(chapter_folder_path):
					raise frappe.PermissionError

				for root, _dirs, files in os.walk(chapter_folder_path):
					if file in files:
						correct_file_path = os.path.join(root, file)
						break

				if correct_file_path and self._is_safe_path(correct_file_path):
					return self._serve_file(correct_file_path)
