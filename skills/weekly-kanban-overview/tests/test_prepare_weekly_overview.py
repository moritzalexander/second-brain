import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare_weekly_overview.py"
SPEC = importlib.util.spec_from_file_location("prepare_weekly_overview", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CarryForwardMondayTests(unittest.TestCase):
    def test_all_carried_cards_are_reset_to_monday(self):
        source = """\
- [ ] Friday root #plan/project/QBR #plan/day/fri #weekly-starred
  - [Reference](https://example.com)
- [/] Tuesday root #plan/day/tue #plan/project/Admin-Core
- [x] Completed parent #plan/project/Team #plan/day/thu
  - [ ] Open child
- [x] Completed root #plan/project/QBR #plan/day/wed
- [-] Cancelled root #plan/project/QBR #plan/day/fri
"""

        carried = MODULE.carry_forward_blocks(source)

        self.assertEqual(
            {MODULE.visible_task_key(block.root) for block in carried},
            {"friday root", "tuesday root", "open child"},
        )
        for block in carried:
            self.assertEqual(re.findall(r"#plan/day/(\w+)", block.root), ["mon"])
        friday = next(block for block in carried if "Friday root" in block.root)
        self.assertIn("#weekly-starred", friday.root)
        self.assertIn("[Reference](https://example.com)", "\n".join(friday.lines))

    def test_merge_preserves_existing_manual_placement(self):
        target = """\
---
week: 2026-W34
---

# Week

- [ ] User-planned Friday task #plan/project/QBR #plan/day/fri
"""
        source = "- [ ] Newly carried task #plan/project/QBR #plan/day/fri\n"
        carried = MODULE.carry_forward_blocks(source)

        merged, count = MODULE.merge_missing_blocks(target, carried)

        self.assertEqual(count, 1)
        self.assertIn("User-planned Friday task #plan/project/QBR #plan/day/fri", merged)
        self.assertIn("Newly carried task #plan/project/QBR #plan/day/mon", merged)

    def test_archive_keeps_current_and_previous_week(self):
        with tempfile.TemporaryDirectory() as temp:
            daily = Path(temp)
            old = daily / "2026-W30-kanban.md"
            previous = daily / "2026-W32-kanban.md"
            current = daily / "2026-W33-kanban.md"
            future = daily / "2026-W34-kanban.md"
            for path in (old, previous, current, future):
                path.write_text(path.name, encoding="utf-8")

            moves = MODULE.archive_old_planning_files(daily, date(2026, 8, 11), dry_run=False)

            self.assertEqual([source.name for source, _ in moves], [old.name])
            self.assertTrue((daily / "Archive" / old.name).exists())
            self.assertTrue(previous.exists())
            self.assertTrue(current.exists())
            self.assertTrue(future.exists())

    def test_first_run_bootstraps_without_a_prior_week(self):
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp)
            (vault / "daily").mkdir()

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--vault",
                    str(vault),
                    "--today",
                    "2026-08-07",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            tasks = vault / "daily" / "2026-W33-kanban-tasks.md"
            board = vault / "daily" / "2026-W33-kanban.md"
            self.assertTrue(tasks.exists())
            self.assertTrue(board.exists())
            self.assertIn("week: 2026-W33", tasks.read_text(encoding="utf-8"))
            self.assertIn("file:2026-W33-kanban-tasks", board.read_text(encoding="utf-8"))
            self.assertIn("Open cards carried: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
