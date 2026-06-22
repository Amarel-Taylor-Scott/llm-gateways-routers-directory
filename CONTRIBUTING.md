# Contributing

This is a curated directory of public **LLM gateways, proxies & routers**.
Listings are pointers to upstream repos/homepages (name, org, category, license)
— no third-party code is vendored.

## Add or update an entry

1. Edit [`data.py`](data.py) — add a `Tool(...)` with the correct category, the
   `open_source` flag, the EXACT license (or `"Proprietary"`), a short note, and
   the canonical link (GitHub repo for OSS, homepage for hosted services). Omit
   anything you can't verify.
2. Run `python main.py generate` to refresh `README.md`.
3. Run `pytest -q`.
4. Open a PR linking the project.

## Quality bar

- Keep the focus on **gateways/proxies/routers** (the layer that routes & manages
  calls across providers) — *not* inference engines or raw provider endpoints.
- Record the EXACT license for OSS tools; mark hosted-only services `Proprietary`.
- `python main.py generate` must leave `README.md` unchanged in CI.
