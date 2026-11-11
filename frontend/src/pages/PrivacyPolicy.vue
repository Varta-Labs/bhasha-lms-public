<template>
	<LegalPage
		:title="__('Privacy Policy')"
		updated="7 September 2026"
		:contents="contents"
	>
		<template #intro>
			<p>
				This Privacy Policy explains how Varta Labs Private Limited, operating
				as Bhasha.io (“Bhasha”, “we”, “us” or “our”), collects, uses, stores
				and shares personal data when you visit or use the learning platform
				at learn.bhasha.io (the “LMS”).
			</p>
		</template>

		<section id="information">
			<h2>1. Information we collect</h2>
			<p>Depending on how you use the LMS, we may collect:</p>
			<ul>
				<li><strong>Account and profile information:</strong> name, email address, username, profile image, language preferences and profile details you choose to provide, such as a biography or social profile links.</li>
				<li><strong>Enrollment and learning activity:</strong> courses and batches you join, your current lesson, lesson completion, progress, video watch duration and related timestamps.</li>
				<li><strong>Assessments and learner content:</strong> quiz attempts, answers and scores; assignment files or responses; programming-exercise submissions; evaluation and certificate records; and posts, comments or replies you submit.</li>
				<li><strong>Billing and transaction information:</strong> billing name, address, telephone number, country, postal code, GSTIN where supplied, course purchased, price, tax, payment status and payment or order identifiers.</li>
				<li><strong>Technical and security information:</strong> IP address, browser and device information, session information, login and audit records, diagnostic data and security logs.</li>
				<li><strong>Communications:</strong> support requests, feedback, notification preferences and other messages you send to us.</li>
			</ul>
		</section>

		<section id="use">
			<h2>2. How we use information</h2>
			<p>We use personal data to create and secure accounts; enroll learners; provide purchased or free course access; remember progress; operate videos, assessments and certificates; process payments and taxes; communicate service information; respond to support requests; prevent fraud and misuse; diagnose problems; improve the LMS; and comply with applicable law.</p>
			<p>Where we ask for consent for an optional purpose, such as promotional email, you may withdraw that consent at any time. Service messages needed to operate your account or deliver a course are not promotional messages.</p>
		</section>

		<section id="payments">
			<h2>3. Payments</h2>
			<p>Payments are processed by <a href="https://razorpay.com/privacy/" target="_blank" rel="noopener noreferrer">Razorpay</a>. Bhasha does not receive or store your complete card number, bank-account credentials or UPI credentials. Razorpay processes payment credentials under its own privacy and security terms.</p>
			<p>We retain billing details, payment and order identifiers, amounts, tax information, invoice information and transaction status as needed to provide access, issue records, handle refunds or disputes, prevent fraud and meet accounting, tax and legal obligations.</p>
		</section>

		<section id="cookies">
			<h2>4. Cookies, telemetry and embedded media</h2>
			<p>The LMS uses cookies and similar browser storage that are necessary for authentication, session continuity, security, preferences and reliable operation. We may also collect limited product-usage and diagnostic events to understand how the LMS is used, measure reliability and improve the learning experience.</p>
			<p>Courses may contain videos or other content embedded from services such as <a href="https://vimeo.com/privacy" target="_blank" rel="noopener noreferrer">Vimeo</a> or <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">YouTube</a>. When embedded content loads, its provider may receive technical information including your IP address, browser or device details and the referring page, and may use cookies or similar storage according to its own privacy policy.</p>
		</section>

		<section id="sharing">
			<h2>5. How information is shared</h2>
			<p>We do not sell personal data. We may share only the information reasonably necessary with service providers that help us run the LMS, including payment processing, video delivery, hosting, data storage, email delivery, security, support and analytics. These providers process information for their contracted service and under their own applicable privacy terms.</p>
			<p>We may also disclose information when required by law, to protect the rights and safety of learners or others, to investigate fraud or abuse, or as part of a merger, acquisition or transfer of the business where appropriate protections continue to apply.</p>
		</section>

		<section id="visibility">
			<h2>6. Learning activity and visibility</h2>
			<p>Authorized instructors, evaluators and LMS administrators may view information relevant to teaching and operating a course, including enrollment, progress, video completion, submissions, scores, evaluations and certificates.</p>
			<p>Profile information and content you choose to post in discussions, comments, reviews or other collaborative areas may be visible to instructors or other learners. Certificate details may be displayed on a verification or profile page when that feature is enabled. Avoid including sensitive personal information in content that other users can see.</p>
		</section>

		<section id="retention">
			<h2>7. Retention and deletion</h2>
			<p>We keep personal data only for as long as it is needed for the purposes described in this policy. Account and learning records may be retained while your account or course access remains active and for a reasonable period afterward to preserve purchased access, progress and certificate records.</p>
			<p>Payment, invoice and tax records are retained for the period required by applicable law. Security logs and backups are retained according to our operational and security schedules. When information is no longer required, we delete or anonymize it, unless continued retention is required for legal compliance, dispute resolution, fraud prevention or enforcement of our agreements.</p>
		</section>

		<section id="security">
			<h2>8. Security</h2>
			<p>We use reasonable technical and organizational safeguards designed to protect personal data, including encrypted network connections, access controls, authentication, logging, backups and restricted administrative access. No online service can guarantee absolute security. If a personal-data breach affects you, we will provide notice when required by applicable law.</p>
		</section>

		<section id="rights">
			<h2>9. Your choices and rights</h2>
			<p>You may request access to personal data associated with your account, correction of inaccurate information, or deletion of information that we are not required to retain. You may also withdraw consent for consent-based processing, opt out of promotional messages, raise a privacy grievance, or nominate another person to exercise applicable rights on your behalf.</p>
			<p>To make a request, email <a href="mailto:hello@bhasha.io?subject=Data%20Privacy%20Policy%20Request">hello@bhasha.io</a> with “Data Privacy Policy Request” in the subject line. We may ask for information needed to verify your identity and locate your account. Some requests may be limited where retention or processing is required by law or is necessary to provide a service you asked us to provide.</p>
		</section>

		<section id="children">
			<h2>10. Children’s privacy</h2>
			<p>Our courses are designed for adult learners. A person under 18 should use the LMS only with the consent and supervision of a parent or legal guardian. A parent or guardian may contact us to ask about, correct or request deletion of a child’s personal data, subject to applicable legal requirements.</p>
		</section>

		<section id="changes">
			<h2>11. Changes and contact</h2>
			<p>We may update this policy as the LMS or applicable requirements change. We will post the revised version here with a new “Last updated” date and, where appropriate, provide an additional notice through the LMS or by email.</p>
			<p>For privacy questions, rights requests or complaints, contact Varta Labs Private Limited at <a href="mailto:hello@bhasha.io">hello@bhasha.io</a>.</p>
			<address>DNO-145/118, BLDG East End B Main, 9th Block Jayanagar, Bengaluru, Karnataka 560069, India.</address>
		</section>
	</LegalPage>
</template>

<script setup lang="ts">
import LegalPage from '@/components/LegalPage.vue'

const contents = [
	{ id: 'information', label: '1. Information we collect' },
	{ id: 'use', label: '2. How we use information' },
	{ id: 'payments', label: '3. Payments' },
	{ id: 'cookies', label: '4. Cookies, telemetry and embedded media' },
	{ id: 'sharing', label: '5. How information is shared' },
	{ id: 'visibility', label: '6. Learning activity and visibility' },
	{ id: 'retention', label: '7. Retention and deletion' },
	{ id: 'security', label: '8. Security' },
	{ id: 'rights', label: '9. Your choices and rights' },
	{ id: 'children', label: '10. Children’s privacy' },
	{ id: 'changes', label: '11. Changes and contact' },
]
</script>
