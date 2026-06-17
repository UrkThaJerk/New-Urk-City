# New-Urk-City

A small Python system for running three legitimate opportunity-scanning agents:

- Yield agent for low-risk cash yield and bank bonus monitoring
- Savings agent for cashback, rebates, settlements, and refund opportunities
- Opportunity agent for lawful earnings like grants, bug bounties, and research studies

## Guardrails

- Agents only discover, score, verify, and prepare opportunities.
- Human approval is always required before opening accounts, moving money, applying, or accepting terms.
- Untrusted or unverifiable opportunities are suppressed.
- Automation phases are intentionally limited to alerts, reminders, and approved prep work.

## Run

```bash
cd /home/runner/work/New-Urk-City/New-Urk-City
PYTHONPATH=src python -m new_urk_city
```

## Test

```bash
cd /home/runner/work/New-Urk-City/New-Urk-City
python -m unittest discover -s tests
```
