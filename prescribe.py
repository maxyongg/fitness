#!/usr/bin/env python3
"""
Retired 2026-09-24. Used to bump RX.asof to today after every drain.

That made the page say "Prescribed today" when nothing had been re-prescribed, which is
how an Upper B on 2026-09-24 left the plan untouched without anyone noticing. RX.asof and
RX.after now move only when prescriptions do: represcribe.py after a phone save, or a
Claude session that re-prescribes by hand.

.github/workflows/drain.yml still calls this, so it stays as a no-op. Delete the call,
and this file, the next time drain.yml is edited.
"""

print("prescribe.py: retired, RX.asof is left to represcribe.py")
