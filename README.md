# Bhasha LMS (public source mirror)

This repository contains the source code for Varta Labs' customized Frappe LMS.
It is published under the GNU Affero General Public License, version 3 or later.

This is a source-only mirror. Operational deployment files, infrastructure
details, credentials, databases, backups, logs, generated bundles, and course or
customer data are deliberately not part of this repository. The application
source and reproducible build inputs are provided separately from that runtime
and operational material.

The mirror is generated from a committed revision of the private operational
repository. The originating revision is recorded in `.public-source-commit`.

## Included source

- `lms/`: Frappe application code, DocType definitions, patches, templates,
  translations, and source assets.
- `frontend/`: Vue/Vite source, build configuration, dependency lockfile, and
  static UI assets.
- Root Python and JavaScript package manifests and lockfiles.
- The complete AGPL license in `license.txt`.

Generated frontend output under `lms/public/frontend` is intentionally omitted;
it is reproducible from `frontend/`.

## Development

Bhasha LMS is a Frappe v15 application and requires the Frappe `payments` app.
A typical development installation is:

```bash
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
bench get-app --branch version-15 https://github.com/frappe/payments
bench get-app https://github.com/Varta-Labs/bhasha-lms-public
bench new-site lms.localhost
bench --site lms.localhost install-app payments
bench --site lms.localhost install-app lms
```

Build the frontend from the app checkout with:

```bash
yarn install
yarn build
```

See `pyproject.toml`, `package.json`, and `frontend/package.json` for dependency
and build details.

## License

Copyright holders retain their respective copyrights. This program is free
software under the GNU Affero General Public License v3 or later. See
`license.txt`.
