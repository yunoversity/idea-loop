# Hiring log

## 2026-08-22 — five hires onboarded (review complete)

Anthony approved hiring rapid-prototyper, ui-designer, test-writer-fixer,
experiment-tracker, ux-researcher (source: contains-studio/agents, GitHub).
Per Anthony's instruction, the CoS reviewed the upstream files for malicious or
misaligned content before onboarding.

**Security review findings — no malicious content.** No injected directives,
no exfiltration or callback endpoints, no credential handling. Two hygiene
issues fixed at onboarding:
- test-writer-fixer declared no tools (would inherit ALL tools) → explicit
  minimal toolset assigned.
- rapid-prototyper contained a mixed-script artifact ("демoing", Cyrillic
  mid-word) — benign upstream typo, but a known obfuscation pattern; removed.

**Misalignments corrected in the onboarded versions** (`.claude/agents/`):
- Virality/TikTok-trend chasing (rapid-prototyper, ui-designer) → replaced
  with assumption-testing focus per goals.md.
- Default reach for paid services (Stripe, Auth0, paid analytics/research
  tools) → no-new-spend rule; free tiers only; escalate needs to Anthony.
- 6-day/week-based timelines → 48-hour SLA cadence.
- experiment-tracker's 1000-users/95%-confidence thresholds → Strong/Weak/
  Failure evidence standards sized for early validation.
- Proactive self-triggering (test-writer-fixer, experiment-tracker) →
  invoked only within Anthony-approved builds, per the autonomy rule.
- ux-researcher assumed it runs studies itself → Anthony conducts all human
  contact; agent arms and debriefs him.

All five bound to CLAUDE.md (prime directive, autonomy rule), goals.md (48h
SLA), and sync discipline. Builds start only from a PRD Anthony explicitly
approves for build. Upstream originals removed after adaptation (retrievable
from contains-studio/agents if ever needed).

**Telegram escalation:** none sent — no major risks found (Anthony's rule:
flag major risks immediately; this review cleared).

**Standing staffing risk:** no dedicated frontend/backend/devops hire;
rapid-prototyper carries the stack and deployment alone. Flag with a re-hire
proposal if an MVP build strains the 48h SLA.
