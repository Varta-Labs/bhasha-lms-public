(() => {
	const focusedAccountPaths = new Set([
		"/update-password",
		"/set-password",
		"/reset-password",
	]);

	const markFocusedFlow = () => {
		const path = window.location.pathname.replace(/\/$/, "") || "/";
		if (focusedAccountPaths.has(path)) {
			document.body.classList.add("bhasha-focused-account-flow");
		}
	};

	const removeFrameworkCredit = (root = document) => {
		if (
			root.matches?.(
				'.powered-by, .footer-powered, [data-powered-by="frappe"]',
			)
		) {
			root.remove();
			return;
		}

		root
			.querySelectorAll(
				'.powered-by, .footer-powered, [data-powered-by="frappe"]',
			)
			.forEach((element) => element.remove());

		root
			.querySelectorAll("footer a, footer span")
			.forEach((element) => {
				if (
					/\b(built|powered)\s+(on|by)\s+frappe\b/i.test(
						element.textContent || "",
					)
				) {
					element.remove();
				}
			});
	};

	const applyBranding = () => {
		markFocusedFlow();
		removeFrameworkCredit();
	};

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", applyBranding, {
			once: true,
		});
	} else {
		applyBranding();
	}

	new MutationObserver((mutations) => {
		for (const mutation of mutations) {
			for (const node of mutation.addedNodes) {
				if (node.nodeType === Node.ELEMENT_NODE) removeFrameworkCredit(node);
			}
		}
	}).observe(document.documentElement, { childList: true, subtree: true });
})();
