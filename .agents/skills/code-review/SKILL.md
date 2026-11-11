---
name: code-review
description: Review wagtail-qrcode changes or a requested area for actionable defects, compatibility regressions, and requirement gaps. Use for a requested code review or an agreed review step.
---

# Code Review

Read and follow [development](../development/SKILL.md) and
the [repository guidelines](../../../AGENTS.md). Consult the [README](../../../README.md)
and local technical skills relevant to the area under review.

A review is read-only unless fixes are also requested. Inspect the existing
checkout without creating a branch or changing files merely to review them.
Return findings in the chat; publishing comments or a GitHub review requires
the user's instruction. Apply the development workflow before implementing
requested fixes.

## Establish the review target

- Identify the original request, acceptance criteria, and intended users before
  judging the implementation. Use linked issues or supplied requirements when
  available. Distinguish an unmet requirement from an unresolved product choice.
- For **change review**, identify the exact diff. For local uncommitted work,
  include staged, unstaged, and relevant untracked files. For a branch or pull
  request, verify the target branch and compare from the merge base; include
  uncommitted work only when it belongs to the requested review. If no target is
  stated, use the current uncommitted work, or the current branch against the
  verified repository default branch when the working tree is clean. State the
  chosen scope. Ask only when ambiguity would materially change the review.
- For a **broader review**, identify the requested feature, directory, or
  concern and its boundaries. Existing defects within that scope are relevant.
- Follow changed behaviour into callers, queries, models, templates, settings,
  migrations, and tests as needed. A small diff can have consequences outside
  its files. Check the previous behaviour before attributing a regression.

## Apply the review priorities

Use these priorities to direct attention, then order findings by actual impact.
Apply the criteria that fit the change and its effect on host Wagtail sites.

| Priority | What to establish |
| --- | --- |
| Requirements and scope | The requested behaviour is complete, relevant edge cases have an intended outcome, and unrelated changes do not obscure review. Identify material design decisions hidden in the implementation. |
| Correctness and regressions | Trace QR generation, downloads, email, or scan redirects through the affected path. Check invalid inputs, error handling, and compatibility with host settings, existing callers, and the relevant tox environments. |
| Security, permissions, and publishing | Check authorization and escaping at the affected boundary. For redirects or downloads, establish how the change handles private or unpublished content and any relevant site boundaries. |
| Data integrity and migrations | Check document or collection updates for partial failures, repeated saves, and compatibility with existing records or revisions. Consider migration requirements when models change. |
| Query performance | Check repeated queries and generation work in affected hooks or requests. Tie performance findings to an affected path or measurement. |
| Accessibility and editor experience | Check keyboard access, labels, feedback, and the affected editor flow. Verify panels and templates on the Wagtail versions affected. |
| Design and maintainability | Prefer existing Wagtail/Django patterns and project conventions. Identify concrete costs from unnecessary abstractions, duplicated rules, misplaced responsibilities, or unjustified dependencies. Tie findings to a failure or maintenance burden rather than personal style. |
| Tests and verification | Check whether coverage demonstrates the requested outcome and would detect the relevant regression, including permission or invalid cases when affected. Identify specific missing scenarios; a low coverage number or absent test alone is not a finding. |
| Documentation and operation | Check that install instructions, host settings, and usage examples match the package behavior. Include dependency or migration notes when they affect package consumers. |

Review test selection using the development skill's verification guidance.
Assess both missing coverage and whether each added test protects a meaningful
project requirement or integration boundary, adds distinct confidence, and has
a proportionate maintenance cost. Flag redundant framework-mechanics tests or
incidental assertions when they add concrete maintenance burden. Preserve useful
integration coverage even when the framework supplies the underlying behaviour.

## Gather evidence

Verify suspected findings against the actual control flow and the affected
framework version. Follow relevant technical skill guidance for API
details. Do not report a hypothetical failure that existing validation,
permissions, or framework behaviour already prevents.

Use focused Django tests, `make test`, or relevant tox environments as needed,
following the development skill's verification guidance. Inspect tests and
rendered output where they can resolve a concern. Preserve the working tree
during verification.
Report each check's result or the specific reason it could not run. A passing
suite supports a review but does not establish that every requirement is met.

Separate confirmed findings from assumptions and questions. When a material
concern cannot be established, explain what evidence or decision is missing
without presenting it as a proven defect. Keep existing test failures distinct
from failures introduced by the reviewed changes.

## Report actionable findings

Lead with findings in severity order. For each finding, provide:

- A short title and severity.
- The precise file and smallest useful line range. In a change review, anchor
  to the relevant changed lines where possible and explain any finding elsewhere.
- The concrete trigger, affected user or operation, and resulting impact.
- Supporting code, reproduction, or check evidence and a concise correction
  direction where useful. Keep uncertain assumptions explicit.

Use severity consistently:

- **P0 — critical:** immediate action is needed for an established, widespread
  outage, severe exposure, or destructive behaviour under normal use.
- **P1 — high:** a serious failure or exposure in a supported flow warrants
  fixing before the change is released.
- **P2 — normal:** a material defect, requirement gap, or maintenance problem
  should be corrected in the normal development cycle.
- **P3 — low:** a minor but concrete problem has limited impact.

Judge severity by impact, reach, and likelihood. Do not invent findings to fill
a quota, repeat one root cause as several findings, or report formatting preferences without an
applicable convention and a concrete consequence.

For change reviews, focus findings on introduced problems and missing required
behaviour. Identify directly relevant pre-existing problems, particularly when
they block verification or safe use.
For broader reviews, report existing problems within the stated scope.

After findings, include material questions or assumptions, verification results
and gaps, and the reviewed scope. Keep the report proportional to the work.
If there are no findings, say **No actionable findings** and state the
verification limits.
