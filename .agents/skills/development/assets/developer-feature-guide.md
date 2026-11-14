# [Feature name]

[Name the package module or integration point responsible for the feature.
Explain what the feature does and which workflow it supports.]

## Wagtail admin workflow

[If editors manage this feature, show where to start in the admin, what content
they create or change, and how they preview, submit for review, or publish it.
Include any required permissions or parent pages and describe where the result
appears. Omit this section when the feature has no editor workflow.]

## Behaviour to preserve

[Describe the rules that matter when changing this feature, such as required
page relationships, content ordering, or what can appear in public results.
Explain why a rule exists when the reason is easy to miss.]

## Where to start in the code

[Link to the main entry point for a typical change and explain how it connects
to the relevant models, templates, or API code. Include the tests that capture
the behaviour.]

## Configuration

[List feature-specific settings, environment variables, and services. Say
which are required and what defaults apply. Link to shared setup or the
relevant example configuration. Use placeholders for secrets. Omit this
section when the feature needs no configuration beyond shared project setup.]

- **Host Wagtail site** [Explain which settings, URLs, or models the site must
  configure and where those settings go.]
- **Local test site** [Describe any overrides or setup steps needed to exercise
  the feature in `tests/testapp/`.]

## Verify a change

[Describe any sample data needed to exercise the feature. Link to the shared
project setup or the configuration section as needed.]

[Give the focused test command and say what it covers. Include manual steps
and their expected results where the tests leave a gap.]
