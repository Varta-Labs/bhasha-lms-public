<template>
	<div class="privacy-page">
		<header class="privacy-page__header">
			<div class="privacy-page__shell privacy-page__header-inner">
				<router-link :to="{ name: 'Courses' }" aria-label="Bhasha.io courses">
					<LMSLogo class="privacy-page__logo" />
				</router-link>
				<router-link :to="{ name: 'Courses' }" class="privacy-page__back">
					<ArrowLeft class="size-4" />
					{{ __('Back to Courses') }}
				</router-link>
			</div>
		</header>

		<main class="privacy-page__shell privacy-page__content">
			<div class="privacy-page__intro">
				<span>{{ __('Bhasha Learning Management System') }}</span>
				<h1>{{ __('Privacy Policy') }}</h1>
				<p class="privacy-page__updated">{{ __('Last updated: 7 September 2026') }}</p>
				<p>
					This Privacy Policy explains how Varta Labs Private Limited, operating
					as Bhasha.io (“Bhasha”, “we”, “us” or “our”), collects, uses, stores
					and shares personal data when you visit or use the learning platform
					at learn.bhasha.io (the “LMS”).
				</p>
			</div>

			<nav class="privacy-page__contents" aria-label="Privacy policy contents">
				<strong>{{ __('On this page') }}</strong>
				<a href="#information">1. Information we collect</a>
				<a href="#use">2. How we use information</a>
				<a href="#payments">3. Payments</a>
				<a href="#cookies">4. Cookies, telemetry and embedded media</a>
				<a href="#sharing">5. How information is shared</a>
				<a href="#visibility">6. Learning activity and visibility</a>
				<a href="#retention">7. Retention and deletion</a>
				<a href="#security">8. Security</a>
				<a href="#rights">9. Your choices and rights</a>
				<a href="#children">10. Children’s privacy</a>
				<a href="#changes">11. Changes and contact</a>
			</nav>

			<div class="privacy-page__sections">
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
			</div>
		</main>
	</div>
</template>

<script setup lang="ts">
import { usePageMeta } from 'frappe-ui'
import { ArrowLeft } from 'lucide-vue-next'
import LMSLogo from '@/components/Icons/LMSLogo.vue'

usePageMeta(() => ({
	title: __('Privacy Policy'),
}))
</script>

<style scoped>
.privacy-page { min-height:100%; background:linear-gradient(180deg,#f8f6ff 0,#fff 20rem); color:#3f3f46; font-family:var(--bhasha-font-sans); }
.privacy-page__shell { width:min(100%,960px); margin-inline:auto; padding-inline:clamp(1rem,4vw,2.5rem); }
.privacy-page__header { position:sticky; z-index:10; top:0; border-bottom:1px solid rgba(108,92,231,.14); background:rgba(255,255,255,.92); backdrop-filter:blur(14px); }
.privacy-page__header-inner { display:flex; min-height:4.5rem; align-items:center; justify-content:space-between; gap:1rem; }
.privacy-page__logo { height:2rem; }
.privacy-page__back { display:inline-flex; align-items:center; gap:.45rem; padding:.55rem .85rem; border-radius:9999px; color:#4a38c2; font-size:.875rem; font-weight:700; }
.privacy-page__back:hover { background:rgba(108,92,231,.09); }
.privacy-page__content { padding-block:clamp(3rem,7vw,5.5rem); }
.privacy-page__intro { max-width:760px; }
.privacy-page__intro > span { color:#6c5ce7; font-size:.75rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.privacy-page__intro h1 { margin-top:.7rem; color:#18181b; font-family:var(--bhasha-font-display); font-size:clamp(2.5rem,6vw,4.5rem); font-weight:800; line-height:1.05; letter-spacing:-.045em; }
.privacy-page__updated { margin-top:1rem!important; color:#71717a; font-size:.875rem; font-weight:650; }
.privacy-page__intro p:last-child { margin-top:1.5rem; color:#52525b; font-size:1.0625rem; line-height:1.75; }
.privacy-page__contents { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.45rem 1.5rem; margin-top:2.5rem; padding:1.5rem; border:1px solid rgba(108,92,231,.18); border-radius:1.25rem; background:rgba(255,255,255,.85); box-shadow:0 18px 45px -35px rgba(61,34,111,.45); }
.privacy-page__contents strong { grid-column:1/-1; margin-bottom:.35rem; color:#18181b; font-family:var(--bhasha-font-display); }
.privacy-page__contents a { color:#5b4acb; font-size:.875rem; line-height:1.5; }
.privacy-page__contents a:hover,.privacy-page__sections a { text-decoration:underline; text-underline-offset:3px; }
.privacy-page__sections { margin-top:3.5rem; }
.privacy-page__sections section { scroll-margin-top:6rem; padding-block:2rem; border-top:1px solid #e4e4e7; }
.privacy-page__sections h2 { color:#18181b; font-family:var(--bhasha-font-display); font-size:clamp(1.35rem,2.5vw,1.7rem); font-weight:800; letter-spacing:-.02em; }
.privacy-page__sections p,.privacy-page__sections li { line-height:1.75; }
.privacy-page__sections p { margin-top:1rem; }
.privacy-page__sections address { margin-top:.75rem; line-height:1.75; font-style:normal; }
.privacy-page__sections ul { display:grid; gap:.75rem; margin-top:1rem; padding-left:1.25rem; list-style:disc; }
.privacy-page__sections strong { color:#27272a; }
.privacy-page__sections a { color:#4a38c2; font-weight:700; }
@media (max-width:639px) { .privacy-page__contents { grid-template-columns:1fr; }.privacy-page__contents strong { grid-column:auto; }.privacy-page__back { padding-inline:.65rem; }.privacy-page__sections section { padding-block:1.5rem; } }
</style>
