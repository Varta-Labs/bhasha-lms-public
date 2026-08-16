"""Import canonical course-exporter JSON into Frappe LMS documents.

Each versioned package is the complete source of truth for its LMS course. The
importer is generic: pass any JSON filename stored in ``lms/course_data``.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

import frappe
from frappe.utils import cint


KANNADA_COURSE_DATA_FILE = "kannada-video-course.json"
DEFAULT_PUBLIC_URL = "https://learn.bhasha.io"
EDITORJS_VERSION = "2.29.0"


def _course_package_path(filename: str) -> Path:
	if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.json", str(filename)):
		raise ValueError("Course filename must be a lowercase slug ending in .json.")
	# Frappe scrubs every extra get_app_path component as a Python module name,
	# which changes filename hyphens to underscores. Resolve the app first, then
	# join the data path without normalization.
	return Path(frappe.get_app_path("lms")) / "course_data" / filename


def _load_course_package(filename: str) -> dict:
	path = _course_package_path(filename)
	with path.open(encoding="utf-8") as handle:
		package = json.load(handle)
	_validate_course_package(package)
	if package["course"]["id"] != path.stem:
		raise ValueError("Package course.id must match its JSON filename.")
	return package


def _validate_course_package(package: dict) -> None:
	if package.get("schemaVersion") != "1.0":
		raise ValueError(f"Unsupported course schema version: {package.get('schemaVersion')!r}")
	if package.get("mode") != "ready":
		raise ValueError("Only course packages exported in ready mode can be imported.")

	course = package.get("course") or {}
	for fieldname in ("id", "lmsCourseId", "title", "description", "modules"):
		if not course.get(fieldname):
			raise ValueError(f"Course package is missing {fieldname!r}.")
	for fieldname in ("id", "lmsCourseId"):
		if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(course[fieldname])):
			raise ValueError(f"Course {fieldname} must be a lowercase slug.")
	settings = course.get("lmsSettings") or {}
	if not settings.get("introVideoUrl") and not settings.get("useFirstLessonVideoAsIntro"):
		raise ValueError("Course package must configure an intro video or first-lesson fallback.")

	module_ids = set()
	lesson_ids = set()
	for module in course["modules"]:
		module_id = module.get("id")
		if not module_id or module_id in module_ids:
			raise ValueError(f"Module IDs must be present and unique; received {module_id!r}.")
		module_ids.add(module_id)
		if not module.get("title") or not module.get("chapters"):
			raise ValueError(f"Module {module_id!r} must have a title and lessons.")
		for lesson in module["chapters"]:
			lesson_id = lesson.get("id")
			if not lesson_id or lesson_id in lesson_ids:
				raise ValueError(f"Lesson IDs must be present and unique; received {lesson_id!r}.")
			lesson_ids.add(lesson_id)
			content_types = {item.get("type") for item in lesson.get("content", [])}
			if not {"video", "slides"}.issubset(content_types):
				raise ValueError(f"Lesson {lesson_id!r} must contain video and slides content.")


def _vimeo_referer(public_url: str) -> str:
	parsed = urlparse(str(public_url).strip())
	if parsed.scheme not in {"http", "https"} or not parsed.netloc:
		raise ValueError("public_url must be an absolute HTTP(S) URL.")
	return f"{parsed.scheme}://{parsed.netloc}/"


def _validate_vimeo_embeds(package: dict, public_url: str) -> list[dict]:
	issues = []
	seen_urls = set()
	referer = _vimeo_referer(public_url)
	intro = _intro_video(package["course"])
	videos = [("course-intro", intro)] if intro else []
	for module in package["course"]["modules"]:
		for lesson in module["chapters"]:
			for item in lesson["content"]:
				if item.get("type") == "video":
					videos.append((lesson["id"], item))
	for lesson_id, item in videos:
		if item.get("provider") != "vimeo" or item.get("url") in seen_urls:
			continue
		seen_urls.add(item["url"])
		try:
			query = urlencode({"url": item["url"]})
			request = Request(
				f"https://vimeo.com/api/oembed.json?{query}",
				headers={"Referer": referer, "User-Agent": "Bhasha-LMS-Vimeo-Preflight/1.0"},
			)
			with urlopen(request, timeout=15) as response:
				payload = json.load(response)
		except (OSError, ValueError) as exc:
			issues.append(
				{
					"lesson": lesson_id,
					"url": item["url"],
					"message": f"Vimeo preflight failed: {exc}",
				}
			)
			continue
		status = payload.get("domain_status_code")
		if status is not None and cint(status) != 200:
			issues.append(
				{
					"lesson": lesson_id,
					"url": item["url"],
					"message": f"Vimeo reports domain_status_code {status} for {referer}.",
				}
			)
	return issues


def preflight_course(filename: str, public_url: str = DEFAULT_PUBLIC_URL) -> dict:
	"""Validate one versioned package and its Vimeo permissions without writing data."""
	frappe.only_for(("System Manager", "Moderator"))
	package = _load_course_package(filename)
	referer = _vimeo_referer(public_url)
	issues = _validate_vimeo_embeds(package, referer)
	lesson_count = sum(len(module["chapters"]) for module in package["course"]["modules"])
	return {
		"valid": not issues,
		"filename": filename,
		"course": package["course"]["lmsCourseId"],
		"public_url": referer.rstrip("/"),
		"module_count": len(package["course"]["modules"]),
		"lesson_count": lesson_count,
		"issues": issues,
	}


def preflight_kannada_video_course(public_url: str = DEFAULT_PUBLIC_URL) -> dict:
	"""Backward-compatible shortcut for the Kannada package."""
	return preflight_course(KANNADA_COURSE_DATA_FILE, public_url=public_url)


def _ensure_category(category_name: str) -> None:
	if not category_name or frappe.db.exists("LMS Category", category_name):
		return
	category = frappe.new_doc("LMS Category")
	category.category = category_name
	category.insert(ignore_permissions=True)


def _intro_video(course_definition: dict) -> dict | None:
	settings = course_definition.get("lmsSettings") or {}
	configured_url = str(settings.get("introVideoUrl") or "").strip()
	if configured_url:
		provider = settings.get("introVideoProvider")
		if not provider:
			hostname = (urlparse(configured_url).hostname or "").lower()
			provider = "vimeo" if "vimeo.com" in hostname else "youtube"
		return {"provider": provider, "url": configured_url}
	if not settings.get("useFirstLessonVideoAsIntro"):
		return None
	first_lesson = course_definition["modules"][0]["chapters"][0]
	return next((item for item in first_lesson["content"] if item.get("type") == "video"), None)


def _course_values(course_definition: dict) -> dict:
	settings = course_definition.get("lmsSettings") or {}
	description = html.escape(str(course_definition.get("description") or ""))
	intro_video = _intro_video(course_definition)
	return {
		"title": course_definition["title"],
		"short_introduction": settings.get("shortIntroduction") or course_definition["description"],
		"description": f"<p>{description}</p>",
		"video_link": _video_embed_url(intro_video) if intro_video else None,
		"image": settings.get("image"),
		"card_gradient": settings.get("cardGradient"),
		"tags": settings.get("tags", ""),
		"category": settings.get("category"),
		"paid_course": cint(settings.get("paidCourse", False)),
		"course_price": settings.get("coursePrice", 0),
		"currency": settings.get("currency"),
		"amount_usd": settings.get("amountUsd"),
		"upcoming": cint(settings.get("upcoming", False)),
		"featured": cint(settings.get("featured", False)),
		"disable_self_learning": cint(settings.get("disableSelfLearning", False)),
		"enable_certification": cint(settings.get("enableCertification", False)),
		"paid_certificate": cint(settings.get("paidCertificate", False)),
		"evaluator": settings.get("evaluator"),
		"timezone": settings.get("timezone"),
		"eyebrow_text": settings.get("eyebrowText"),
		"trust_badges": settings.get("trustBadges"),
		"course_highlights_json": settings.get("courseHighlightsJson"),
		"learning_outcomes_json": settings.get("learningOutcomesJson"),
		"faqs_json": settings.get("faqsJson"),
		"testimonials_json": settings.get("testimonialsJson"),
	}


def _migrate_course_route(course_definition: dict) -> str | None:
	settings = course_definition.get("lmsSettings") or {}
	old_name = settings.get("replacesLmsCourseId")
	new_name = course_definition["lmsCourseId"]
	if not old_name or old_name == new_name or not frappe.db.exists("LMS Course", old_name):
		return None
	if frappe.db.exists("LMS Course", new_name):
		raise ValueError(
			f"Cannot replace {old_name!r}: target LMS Course {new_name!r} already exists."
		)
	frappe.rename_doc("LMS Course", old_name, new_name, force=True)
	return old_name


def _get_or_create_course(course_definition: dict, publish: int | None):
	settings = course_definition.get("lmsSettings") or {}
	stable_name = course_definition["lmsCourseId"]
	category = settings.get("category")
	_ensure_category(category)

	existing = frappe.db.exists("LMS Course", stable_name)
	created = not bool(existing)
	course = frappe.get_doc("LMS Course", existing) if existing else frappe.new_doc("LMS Course")
	if created:
		course.name = stable_name
	course.set(
		"instructors",
		[{"instructor": instructor} for instructor in settings.get("instructors", ["Administrator"])],
	)
	course.set("related_courses", [])

	values = _course_values(course_definition)
	if publish is not None:
		values["published"] = cint(publish)
		if not cint(publish):
			values.update({"published_on": None, "status": "In Progress", "notification_sent": 0})
	elif created:
		values["published"] = cint(settings.get("publishedOnCreate", False))
	course.update(values)
	if created:
		course.insert(ignore_permissions=True)
	else:
		course.save(ignore_permissions=True)
	return course, created


def _get_or_create_chapter(course, module: dict):
	existing = frappe.db.exists(
		"Course Chapter",
		{"course": course.name, "title": module["title"]},
	)
	created = not bool(existing)
	chapter = frappe.get_doc("Course Chapter", existing) if existing else frappe.new_doc("Course Chapter")
	chapter.update(
		{
			"course": course.name,
			"title": module["title"],
			"is_scorm_package": 0,
			"scorm_package": None,
			"scorm_package_path": None,
			"manifest_file": None,
			"launch_file": None,
		}
	)
	if created:
		chapter.insert(ignore_permissions=True)
	else:
		chapter.save(ignore_permissions=True)
	return chapter, created


def _video_embed_url(video: dict) -> str:
	url = str(video["url"])
	provider = video["provider"]
	parsed = urlparse(url)
	if provider == "vimeo":
		parts = [part for part in parsed.path.split("/") if part]
		if not parts or not re.fullmatch(r"\d+", parts[0]):
			raise ValueError(f"Invalid Vimeo URL: {url!r}")
		embed = f"https://player.vimeo.com/video/{parts[0]}"
		if len(parts) > 1:
			embed += f"?h={parts[1]}"
		return embed
	if provider == "youtube":
		video_id = parse_qs(parsed.query).get("v", [None])[0]
		if not video_id and parsed.hostname == "youtu.be":
			video_id = parsed.path.strip("/")
		if not video_id and parsed.hostname and "youtube.com" in parsed.hostname:
			parts = [part for part in parsed.path.split("/") if part]
			if len(parts) > 1 and parts[0] in {"embed", "shorts"}:
				video_id = parts[1]
		if not video_id:
			raise ValueError(f"Invalid YouTube URL: {url!r}")
		return f"https://www.youtube.com/embed/{video_id}"
	return url


def _lesson_content(lesson_definition: dict) -> dict:
	video = next(item for item in lesson_definition["content"] if item["type"] == "video")
	slides = next(item for item in lesson_definition["content"] if item["type"] == "slides")
	title = html.escape(str(lesson_definition["title"]))
	description = html.escape(str(lesson_definition.get("description") or ""))
	video_description = html.escape(str(video.get("description") or ""))
	slides_description = html.escape(str(slides.get("description") or ""))
	slides_url = str(slides["url"])
	slides_embed = f"https://docs.google.com/presentation/d/{slides['presentationId']}/embed"
	duration = cint(lesson_definition.get("estimatedDurationMinutes"))

	blocks = [
		{"type": "header", "data": {"text": title, "level": 2}},
		{"type": "paragraph", "data": {"text": description}},
	]
	if duration:
		blocks.append(
			{
				"type": "paragraph",
				"data": {"text": f"<strong>Estimated lesson time:</strong> {duration} minutes"},
			}
		)
	blocks.extend(
		[
			{"type": "header", "data": {"text": "Watch the lesson", "level": 3}},
			{"type": "paragraph", "data": {"text": video_description}},
			{
				"type": "embed",
				"data": {
					"service": video["provider"],
					"source": video["url"],
					"embed": _video_embed_url(video),
					"width": 580,
					"height": 320,
					"caption": video.get("title") or lesson_definition["title"],
				},
			},
			{"type": "header", "data": {"text": "Lesson presentation", "level": 3}},
			{"type": "paragraph", "data": {"text": slides_description}},
			{
				"type": "embed",
				"data": {
					"service": "slidesPublic",
					"source": slides_url,
					"embed": slides_embed,
					"width": 580,
					"height": 320,
					"caption": slides.get("title") or lesson_definition["title"],
				},
			},
			{
				"type": "paragraph",
				"data": {
					"text": (
						f'<a href="{html.escape(slides_url, quote=True)}" target="_blank" '
						'rel="noopener noreferrer">Open the presentation in a new tab</a>'
					)
				},
			},
		]
	)
	return {"time": 0, "blocks": blocks, "version": EDITORJS_VERSION}


def _get_or_create_lesson(course, chapter, lesson_definition: dict, include_in_preview: bool):
	filters = {
		"course": course.name,
		"chapter": chapter.name,
		"title": lesson_definition["title"],
	}
	existing = frappe.db.exists("Course Lesson", filters)
	created = not bool(existing)
	lesson = frappe.get_doc("Course Lesson", existing) if existing else frappe.new_doc("Course Lesson")
	lesson.update(
		{
			"course": course.name,
			"chapter": chapter.name,
			"title": lesson_definition["title"],
			"include_in_preview": cint(include_in_preview),
			"content": json.dumps(_lesson_content(lesson_definition), ensure_ascii=False),
			"body": None,
			"youtube": None,
			"quiz_id": None,
			"question": None,
			"file_type": None,
			"instructor_notes": None,
			"instructor_content": None,
			"is_scorm_package": 0,
		}
	)
	if created:
		lesson.insert(ignore_permissions=True)
	else:
		lesson.save(ignore_permissions=True)
	return lesson, created


def _delete_lesson_discussions(lesson_names: set[str]) -> None:
	if not lesson_names:
		return
	topics = frappe.get_all(
		"Discussion Topic",
		filters={"reference_doctype": "Course Lesson", "reference_docname": ("in", tuple(lesson_names))},
		pluck="name",
	)
	if topics:
		frappe.db.delete("Discussion Reply", {"topic": ("in", tuple(topics))})
		frappe.db.delete("Discussion Topic", {"name": ("in", tuple(topics))})


def _purge_obsolete_curriculum(course, active_chapter_names: set[str], active_lesson_names: set[str]) -> dict:
	"""Permanently remove curriculum records absent from the source package."""
	all_chapter_names = set(
		frappe.get_all("Course Chapter", filters={"course": course.name}, pluck="name")
	)
	all_lesson_names = set(
		frappe.get_all("Course Lesson", filters={"course": course.name}, pluck="name")
	)
	obsolete_chapters = all_chapter_names - active_chapter_names
	obsolete_lessons = all_lesson_names - active_lesson_names
	if not obsolete_lessons and not obsolete_chapters:
		return {"deleted_chapters": [], "deleted_lessons": []}

	if obsolete_lessons:
		lesson_filter = {"lesson": ("in", tuple(obsolete_lessons))}
		quiz_names = frappe.get_all("LMS Quiz", filters=lesson_filter, pluck="name")
		if quiz_names:
			frappe.db.delete("LMS Quiz Submission", {"quiz": ("in", tuple(quiz_names))})
			for quiz_name in quiz_names:
				frappe.delete_doc("LMS Quiz", quiz_name, ignore_permissions=True, force=True)
		for doctype in (
			"LMS Course Progress",
			"LMS Video Watch Duration",
			"LMS Lesson Note",
			"LMS Assignment Submission",
			"Scheduled Flow",
		):
			frappe.db.delete(doctype, lesson_filter)
		frappe.db.set_value(
			"LMS Enrollment",
			{"course": course.name, "current_lesson": ("in", tuple(obsolete_lessons))},
			{"current_lesson": None, "progress": 0},
			update_modified=False,
		)
		_delete_lesson_discussions(obsolete_lessons)
		for lesson_name in sorted(obsolete_lessons):
			frappe.delete_doc("Course Lesson", lesson_name, ignore_permissions=True, force=True)

	for chapter_name in sorted(obsolete_chapters):
		frappe.delete_doc("Course Chapter", chapter_name, ignore_permissions=True, force=True)

	return {
		"deleted_chapters": sorted(obsolete_chapters),
		"deleted_lessons": sorted(obsolete_lessons),
	}


def _purge_all_curriculum(course) -> dict:
	"""Clear every curriculum record during a configured course replacement."""
	course.reload()
	course.set("chapters", [])
	course.lessons = 0
	course.save(ignore_permissions=True)
	return _purge_obsolete_curriculum(course, set(), set())


def _sync_curriculum(course, course_definition: dict) -> dict:
	chapter_docs = []
	created_chapters = []
	created_lessons = []
	active_lesson_names = set()

	for module_index, module in enumerate(course_definition["modules"]):
		chapter, chapter_created = _get_or_create_chapter(course, module)
		if chapter_created:
			created_chapters.append(chapter.name)

		lesson_docs = []
		for lesson_index, lesson_definition in enumerate(module["chapters"]):
			lesson, lesson_created = _get_or_create_lesson(
				course,
				chapter,
				lesson_definition,
				include_in_preview=module_index == 0 and lesson_index == 0,
			)
			lesson_docs.append(lesson)
			active_lesson_names.add(lesson.name)
			if lesson_created:
				created_lessons.append(lesson.name)

		chapter.set("lessons", [])
		for lesson in lesson_docs:
			chapter.append("lessons", {"lesson": lesson.name})
		chapter.save(ignore_permissions=True)
		chapter_docs.append(chapter)

	active_chapter_names = {chapter.name for chapter in chapter_docs}
	course.reload()
	course.set("chapters", [])
	for chapter in chapter_docs:
		course.append("chapters", {"chapter": chapter.name})
	course.lessons = len(active_lesson_names)
	course.save(ignore_permissions=True)
	deleted = _purge_obsolete_curriculum(course, active_chapter_names, active_lesson_names)

	return {
		"chapters": [chapter.name for chapter in chapter_docs],
		"lessons": [lesson.lesson for chapter in chapter_docs for lesson in chapter.lessons],
		"created_chapters": created_chapters,
		"created_lessons": created_lessons,
		**deleted,
	}


def import_course(
	filename: str,
	publish: int | None = None,
	validate_remote: int = 1,
	public_url: str = DEFAULT_PUBLIC_URL,
) -> dict:
	"""Fully synchronize one production course from a versioned package.

	Existing publication state is preserved when ``publish`` is omitted. Pass
	``publish=0`` or ``publish=1`` explicitly to override it.
	"""
	frappe.only_for(("System Manager", "Moderator"))
	package = _load_course_package(filename)
	if cint(validate_remote):
		issues = _validate_vimeo_embeds(package, public_url)
		if issues:
			raise ValueError(
				f"Remote video preflight failed for {len(issues)} video(s). "
				"Update Vimeo embed privacy before importing."
			)
	course_definition = package["course"]
	try:
		renamed_from = _migrate_course_route(course_definition)
		course, course_created = _get_or_create_course(course_definition, publish)
		replaced_curriculum = _purge_all_curriculum(course) if renamed_from else None
		result = _sync_curriculum(course, course_definition)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		raise
	return {
		"course": course.name,
		"course_title": course.title,
		"course_created": course_created,
		"renamed_from": renamed_from,
		"replaced_curriculum": replaced_curriculum,
		"published": cint(course.published),
		"source_export_id": package["exportId"],
		"course_url": f"/lms/courses/{course.name}",
		"public_url": _vimeo_referer(public_url).rstrip("/"),
		**result,
	}


def import_kannada_video_course(
	publish: int | None = None,
	validate_remote: int = 1,
	public_url: str = DEFAULT_PUBLIC_URL,
) -> dict:
	"""Backward-compatible shortcut for the Kannada package."""
	return import_course(
		KANNADA_COURSE_DATA_FILE,
		publish=publish,
		validate_remote=validate_remote,
		public_url=public_url,
	)
