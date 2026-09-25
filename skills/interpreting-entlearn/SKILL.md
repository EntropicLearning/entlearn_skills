---
name: interpreting-entlearn
description: Interpret entlearn feature relevance, active features, learned feature, instance or output weights, inlier/outlier scores, effective dimensions, reconstruction, affiliations, parameter counts, or fitted values. Prefer public scikit-learn adapter queries; route Network-only inspection to using-entlearn-advanced.
---

# Interpret a fitted entlearn model

This skill turns a fitted adapter query into a scientifically bounded interpretation. It
holds the workflow; the entlearn documentation holds the facts, and
[interpreting a fit](https://entropiclearning.github.io/entlearn/0.1.0/guide/interpreting/)
states what each query measures. Links point at the documentation for entlearn 0.1.0, this
release's compatibility tag, and
[`llms.txt`](https://entropiclearning.github.io/entlearn/0.1.0/llms.txt) lists every page as
Markdown. When the installed entlearn version differs, replace `0.1.0` in each link with the
installed version and follow that version's pages instead.

## 1. Define the quantity and question

State the scientific question before selecting a query. Separate parameter
participation, fitted-data diagnostics, query-time diagnostics, and predictive
performance. Read [what each query measures](https://entropiclearning.github.io/entlearn/0.1.0/guide/interpreting/#what-each-query-measures)
for the matching public surface and its limits.

**Complete when:** one requested quantity and the scientific comparison it informs are
explicit.

## 2. Preserve the fitted contract

Query the fitted estimator, not a manually rebuilt `Network`. Preserve its
preprocessing, schema, column names and order, categorical vocabularies,
computation dtype/device, and fitted prediction policy. Pass a replacement prediction
policy only when the comparison deliberately changes the complete query policy.

Prefer adapter methods and properties. If the requested value exists only through
`Network.inspect(...)` or another direct `Network` operation, route the task to
`using-entlearn-advanced`.

**Complete when:** input validation passes through the adapter and the query uses the
intended fitted policy.

## 3. Obtain and validate the result

Call the narrowest public query. Check shape, row or feature alignment, availability of
retained training state, and any precondition the query table names. Keep feature labels
attached to reported values. For mixed-data reconstruction and comparisons across rows,
features, models or refits, follow
[reconstruction of mixed data](https://entropiclearning.github.io/entlearn/0.1.0/guide/interpreting/#reconstruction-of-mixed-data)
and [comparisons](https://entropiclearning.github.io/entlearn/0.1.0/guide/interpreting/#comparisons).

**Complete when:** the requested quantity is obtained through the public API and
alignment or availability assumptions have been checked.

## 4. Interpret without substitution

State what generated the value and what it cannot establish, using
[what the values do not establish](https://entropiclearning.github.io/entlearn/0.1.0/guide/interpreting/#what-the-values-do-not-establish)
for the quantity at hand. Relate the result to held-out performance, perturbation evidence,
domain knowledge, or replicate stability as appropriate. Use causal or scientific importance
language only when the study design supports it.

**Complete when:** the semantic meaning and limitations are stated and the result is
tied back to the scientific question without overclaiming.
