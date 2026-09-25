---
name: debugging-entlearn
description: Diagnose entlearn warnings, exceptions, invalid fits, failed convergence, numerical faults, schema or lifecycle errors, and predictions inconsistent with the fitted policy.
---

# Debugging entlearn

Diagnose from evidence and keep valid work moving. Use public `entlearn` namespaces only.
After the immediate fault is classified, invoke `tuning-entlearn` for a poor score or
sensitivity question.

This skill holds the workflow; the entlearn documentation holds the facts, and
[troubleshooting](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/) states what each warning and failure means.
Links point at the documentation for entlearn 0.1.0, this release's compatibility tag, and
[`llms.txt`](https://entropiclearning.github.io/entlearn/0.1.0/llms.txt) lists every page as Markdown, including the
[glossary](https://entropiclearning.github.io/entlearn/0.1.0/concepts/glossary/) and [concepts](https://entropiclearning.github.io/entlearn/0.1.0/concepts/). When the installed entlearn
version differs, replace `0.1.0` in each link with the installed version and follow that
version's pages instead.

Guidance statuses in this skill mean:

- **Required**: needed for a valid diagnosis.
- **Recommended**: the normal next action unless evidence rules it out.
- **Problem-dependent**: use only when the symptom reaches that branch.

## Procedure

1. **Required — preserve the observation.** Record the full warning or exception,
   traceback, package version, estimator or `Recipe`, preprocessing and observed ranges,
   dtype and device, all random seeds, data shapes and schema, fit diagnostics and loss
   history, and the exact prediction policy
   ([where to look first](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/#where-to-look-first)).
   Retain the failing configuration and fitted object without overwriting it. Completion: another researcher can distinguish the
   failing run from every later trial.

2. **Required — classify before changing controls.** Separate:
   - input/schema or lifecycle rejection
     ([schema and target mismatches](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/#schema-and-target-mismatches),
     [what loading checks](https://entropiclearning.github.io/entlearn/0.1.0/guide/networks/#what-loading-checks));
   - `LossIncreaseWarning` ([warnings](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/#warnings));
   - non-convergence at the iteration budget
     ([warnings](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/#warnings));
   - numerical sensitivity
     ([scale, weights and hard assignments](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/#scale-weights-and-hard-assignments));
   - a valid fit with poor score or surprising predictions
     ([unstable or disappointing predictions](https://entropiclearning.github.io/entlearn/0.1.0/guide/troubleshooting/#unstable-or-disappointing-predictions),
     [fitting and prediction controls](https://entropiclearning.github.io/entlearn/0.1.0/guide/hyperparameters/#fitting-and-prediction-controls)).

   Read the linked section for the matching branch. Completion: the symptom has one primary class and the evidence supporting it
   is named.

3. **Required — quarantine a loss increase.** Fitting uses exact block-coordinate
   updates, so a significant loss increase is an immediate red flag, not ordinary
   optimiser noise. Warn the user that the fit is invalid evidence. Preserve it for
   diagnosis, but exclude its scores, predictions, reconstructions, inspections, and
   derived conclusions from the wider analysis. Continue the requested job with
   unaffected fits or configurations where possible. Completion: invalid and trustworthy
   outputs are explicitly separated.

4. **Required — reproduce and minimise.** Re-run with the same seed, dtype, device,
   tensors, `Recipe`, stopping controls, initialisation count, and prediction policy.
   Minimise one dimension at a time while retaining the symptom: rows, columns, blocks,
   categorical features, missingness, dtype/device, initial state, or continuation step.
   Preserve the first failing and nearest passing cases. Completion: either the cause is
   fixed, or a minimal configuration and diagnostics reproduce it.

5. **Recommended — report an actionable library failure.** For a reproducible
   `LossIncreaseWarning` or likely entlearn defect, recommend that the user authorise a
   public entlearn issue containing the minimal data or synthetic reproduction, package
   version, platform, dtype/device, seed, `Recipe`, call, complete warning, diagnostics,
   and loss history. Never post automatically or expose private data. Completion: the
   proposed report is reproducible and publication remains a user decision.

6. **Problem-dependent — tune only trustworthy fits.** Treat one poor score as a tuning
   question before concluding that entropic learning is unsuitable. Once the immediate
   diagnostic check passes, invoke `tuning-entlearn`; compare seeds or initialisations,
   scaling, model capacity, temperatures, and prediction policy there. Completion: tuning
   consumes no quarantined output.

## Completion gate

Finish only when the symptom is classified; failing evidence is preserved; trustworthy
outputs are separated from invalid ones; the cause is fixed or narrowed to a minimal,
actionable report; and the wider requested work has continued wherever its evidence
remains valid.
