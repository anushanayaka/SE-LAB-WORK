

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

folder = Path(".")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="ReportText", fontName="Courier",
    fontSize=7, leading=9, wordWrap="CJK"
))

reports = [
    ("pylint_before.txt", "pylint_report_before.pdf"),
    ("pylint_after.txt", "pylint_report_after.pdf"),
    ("bandit_before.txt", "bandit_report_before.pdf"),
    ("bandit_after.txt", "bandit_report_after.pdf"),
    ("flake8_before.txt", "flake8_report_before.pdf"),
    ("flake8_after.txt", "flake8_report_after.pdf"),
]

def make_pdf(filename, title, content):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for line in content.splitlines():
        story.append(Preformatted(line or " ", styles["ReportText"]))
    doc.build(story)
    print("Created:", filename)

for source, target in reports:
    path = folder / source
    if path.exists():
        make_pdf(target, source.replace(".txt", "").replace("_", " ").title(),
                 path.read_text(encoding="utf-8", errors="replace"))
    else:
        print("Missing:", source)

issues = """Lab 5: Static Code Analysis - Issue Table

Issue | Fix / Status
Unsafe eval() | Replaced with numeric surcharge calculation.
os.system() | Removed shell execution.
Hard-coded secret | Changed to environment variable lookup.
Weak PIN randomness | Changed to secrets-based generation.
Mutable default list | Changed default to None.
Broad exception | Changed to KeyError.
Unused variable | Removed airport_fee.
Flake8 | Three long-line warnings remain in the observed report.
Pylint | Last observed score: 5.50/10; further fixes required.
Bandit | Last observed report: No issues identified."""

reflection = """Lab 5: Reflection

1. What is static code analysis?
Static code analysis examines source code without executing it to find
potential bugs, security problems, and style violations.

2. What did the tools identify?
Pylint identified naming, documentation, and code-structure issues.
Bandit initially identified risky code patterns. Flake8 identified
formatting issues.

3. What did you learn?
I learned to run Pylint, Bandit, and Flake8, save reports, and correct
several code issues. Static analysis helps improve quality but does
not replace program testing.

Current observed status:
Bandit after: No issues identified.
Flake8 after: Three long-line warnings remain.
Pylint after: 5.50/10; the required score above 9.5 is not yet achieved."""

make_pdf("issue_table.pdf", "Issue Table", issues)
make_pdf("reflection.pdf", "Reflection", reflection)
print("Finished creating available PDFs.")
