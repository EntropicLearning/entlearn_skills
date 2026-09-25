---
name: using-entlearn-advanced
description: "Use for direct entlearn Network work: tensor-native data, categorical tensors, distribution targets, partially missing multi-output targets, custom Network optimisation or validation, initial-state transfer, native persistence, direct Network continuation, and detailed prediction policy or state inspection."
---

# Using entlearn advanced

Direct `Network` use is an explicit lifecycle choice. The scikit-learn adapters remain the
ordinary interface, including for manifold inputs. Use public `entlearn` namespaces only.
Invoke `using-entlearn` for suitability, model design and evidence.

This skill holds the workflow; the entlearn documentation holds the facts. Links point at
the documentation for entlearn 0.1.0, this release's compatibility tag, and
[`llms.txt`](https://entropiclearning.github.io/entlearn/0.1.0/llms.txt) lists every page as
Markdown. When the installed entlearn version differs, replace `0.1.0` in each link with the
installed version and follow that version's pages instead.

Guidance statuses are **required**, **recommended**, and **problem-dependent**.

## Procedure

1. **Required — justify the boundary.** Name the adapter limitation requiring direct
   `Network`: tensor-native control; distribution-valued classification targets; direct
   categorical tensors; partially missing multi-output regression; custom
   optimisation/validation; initial-state capture or transfer; native persistence;
   continuation directly on `Network`; or detailed prediction/state queries. Manifold
   input and estimator `warm_start="resume"` or `"fine_tune"` alone are not sufficient
   because adapters support them. Completion: one concrete requirement cannot be met
   cleanly through the adapter.

2. **Required — describe, then fit.** Create an immutable `Recipe` with `Recipe.chain(...)`
   within the [shapes a model can have](https://entropiclearning.github.io/entlearn/0.1.0/guide/package/#what-shapes-can-a-model-have),
   then fit it as [using Networks](https://entropiclearning.github.io/entlearn/0.1.0/guide/networks/)
   describes. Completion: the recipe is compatible with the staged tensor schema and no
   fitted state is mistaken for configuration.

3. **Required — preserve tensor semantics.** Keep dtype, device, row and feature shapes,
   categorical feature order/cardinalities, target meaning, missingness, and recipe
   compatibility explicit across fit and query calls; check each against
   [expected input shapes](https://entropiclearning.github.io/entlearn/0.1.0/guide/networks/#expected-input-shapes).
   Completion: every tensor has a documented shape, dtype, device, and semantic mapping.

4. **Required — own advanced selection.** For custom validation or tuning, define the
   data splits, leakage boundary, selection loss, seeds/initialisations, and retained
   artefacts. Prefer the selection controls on `Network.fit`
   ([select an initialisation with a Network](https://entropiclearning.github.io/entlearn/0.1.0/guide/model_selection/#select-an-initialisation-with-a-network))
   before writing external orchestration. Coupling defaults to M; compare it against S as
   one more hyperparameter when the search warrants it. A single prediction pass is the
   default; iterative prediction is problem-dependent. Completion: selection and
   prediction policies are deliberate and reproducible.

5. **Problem-dependent — plan state lifecycle.** Before initialisation transfer,
   persistence, resume, or fine-tuning, choose one operation: resume the same logical fit,
   fine-tune on compatible data, or start a fresh fit from captured state. Read
   [predict, continue, or start again](https://entropiclearning.github.io/entlearn/0.1.0/guide/networks/#predict-continue-or-start-again)
   and [save the network](https://entropiclearning.github.io/entlearn/0.1.0/guide/networks/#save-the-network)
   for each operation's requirements. Prefer estimator `warm_start` for ordinary tabular
   continuation, so fitted column, category and label meanings stay with the model.
   Completion: the artefact capability and next operation agree, the source object remains
   preserved, and the saved artefact is explicitly prediction-only or resumable.

6. **Required — query and report.** Use `predict`, `predict_with_details`, `inspect`,
   `reconstruct`, or `score_samples` only for the needed result
   ([inspect a prediction](https://entropiclearning.github.io/entlearn/0.1.0/guide/networks/#inspect-a-prediction)).
   Report unavailable details, omitted row-bound state, unretained members, and
   prediction-policy overrides as limitations. Completion: the requested operation
   succeeds through the public API and its artefact/query limits are explicit.

## Completion gate

Finish only when direct-interface use is justified; tensor/schema semantics and the state
lifecycle are valid; the requested public-API operation is complete; and every artefact or
query limitation, including any unavailable reproducibility guarantee, is reported.
