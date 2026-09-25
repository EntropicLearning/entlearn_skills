---
name: using-entlearn
description: Fit and use entlearn EON classifiers or regressors; invoke for entlearn experiment design, entropy-optimal networks, Recipe choices, EON prediction, or deciding whether entlearn suits a dataset. Routes tuning, interpretation, debugging, and direct Network work to specialised skills.
---

# Using entlearn

Use the scikit-learn-compatible `EONClassifier` or `EONRegressor`. Assume prediction is the usual goal, then surface reconstruction and fitted-model inspection when they answer the research question. Keep generic preprocessing, splitting, scoring and pipeline advice with the project's normal ML workflow.

## Documentation

This skill holds the workflow; the entlearn documentation holds the facts. Links below point at the documentation for entlearn 0.1.0, this release's compatibility tag. [`llms.txt`](https://entropiclearning.github.io/entlearn/0.1.0/llms.txt) lists every page as Markdown. When the installed entlearn version differs, replace `0.1.0` in each link with the installed version and follow that version's pages instead. The [glossary](https://entropiclearning.github.io/entlearn/0.1.0/concepts/glossary/) and [notation](https://entropiclearning.github.io/entlearn/0.1.0/concepts/notation/) settle any ambiguous term, dimension or model object; the [concepts](https://entropiclearning.github.io/entlearn/0.1.0/concepts/) pages state the mathematics.

## Workflow

### 1. Establish the public environment

Inspect the project files, installed package metadata, imports and existing experiment before asking the user for facts already available. Record the entlearn version and whether the public names used below exist.

If entlearn is absent, use the project's existing package manager to add `entlearn[sklearn]` ([installation](https://entropiclearning.github.io/entlearn/0.1.0/guide/installation/)). Ask before upgrading entlearn or changing a version constraint. If the installed API differs from this skill's compatibility tag, prefer that version's public API and documentation and state the mismatch.

**Complete when:** the package version, package manager, task type and available public adapter have been verified.

### 2. Check suitability and data meaning

Identify `T` observations, total `D` features, target shape, continuous and categorical columns, and the user's prediction objective. Read [suitability and scaling](https://entropiclearning.github.io/entlearn/0.1.0/guide/suitability/) for small-data, high-dimensional, runtime, limitation or method-comparison decisions.

**Complete when:** every feature and target has a declared meaning and the expected cost and limitations are acceptable.

### 3. Design the first Recipe

Read [a recommended starting point](https://entropiclearning.github.io/entlearn/0.1.0/guide/hyperparameters/#a-recommended-starting-point) before choosing blocks, cluster counts, coupling, temperatures, weights, depth, manifold input or prediction policy. Treat its rules for a valid model as required, its first experiment as the recommended baseline, and its problem-dependent choices as needing evidence. [Package and Recipes](https://entropiclearning.github.io/entlearn/0.1.0/guide/package/) describes the blocks and the shapes a model can have.

Build an immutable classification or regression `Recipe`, then pass it to the matching adapter. Use the shallow standard-input baseline unless known structure justifies another choice (or the user has explicitly requested it). Leave coupling at its default unless the user asks for a specific one; comparing M against S belongs to `tuning-entlearn`.

**Complete when:** the Recipe satisfies the rules for a valid model, cluster counts are explicit, and every departure from the recommended baseline has a problem-specific reason.

### 4. Fit robustly through the adapter

Construct `EONClassifier(recipe, ...)` or `EONRegressor(recipe, ...)` as [using estimators](https://entropiclearning.github.io/entlearn/0.1.0/guide/estimators/) describes. Scale continuous features and regression targets, preserve DataFrame column meanings where available, and declare categorical features through the adapter. Use multiple initialisations and make their randomness reproducible by setting `random_state`. Decide deliberately whether supplied `sample_weight` should stay fixed or seed learned instance weights ([sample and class weights](https://entropiclearning.github.io/entlearn/0.1.0/guide/estimators/#sample-and-class-weights)).

Fit through the estimator API. Treat warnings, non-finite values, failure to converge, or unstable selection as evidence to investigate rather than suppress. Invoke `debugging-entlearn` for failed fits, numerical problems, unexpected staging, convergence or prediction behaviour. Invoke `tuning-entlearn` for hyperparameter search, initialisation selection, validation design or performance refinement.

For later fits, keep ordinary continuation on the adapter through `warm_start`; read [refit and reuse](https://entropiclearning.github.io/entlearn/0.1.0/guide/estimators/#refit-and-reuse) before continuing an estimator. Use `using-entlearn-advanced` only when the task needs the corresponding operation directly on a `Network`.

**Complete when:** the fitted estimator predicts successfully, the initialisation policy is recorded, and `n_iter_`, `loss_curve_` and any warnings have been checked.

### 5. Predict with the fitted policy

Use `predict` (`predict_proba` for classification probabilities). Keep the fitted prediction policy unless evidence supports a complete `PredictConfig` override ([hyperparameters](https://entropiclearning.github.io/entlearn/0.1.0/guide/hyperparameters/#fitting-and-prediction-controls), [prediction and calibration](https://entropiclearning.github.io/entlearn/0.1.0/concepts/prediction/)). Preserve fitted column order, categories, units, dtype policy and feature scaling at prediction time.

**Complete when:** prediction shape and class or target order are verified, and any policy override is explicit and justified.

### 6. Surface inspection options

Mention the public estimator queries in [what each query measures](https://entropiclearning.github.io/entlearn/0.1.0/guide/interpreting/#what-each-query-measures) if they appear relevant, with `network_` as the fitted lower-level object, not the primary workflow.

Invoke `interpreting-entlearn` when explaining these values, comparing fitted structure, interpreting reconstruction, weights or affiliations, or making scientific claims from a fit. Keep routine inspection on the estimator: reaching through `network_` to reproduce an adapter query loses the tabular mapping.

Route tensor-first fitting, direct `Network` fitting or calls, custom retained-state work, low-level continuation, detailed prediction results, or unsupported adapter requirements to `using-entlearn-advanced`.

**Complete when:** the result includes the requested prediction outcome, the useful inspection route, and a clear boundary between descriptive model quantities and held-out predictive evidence.

## Evidence

For claims about released behaviour, use the matching public entlearn API and source first, then its documentation and examples, then this skill's recommendations, and finally research papers. Cite papers from the [literature](https://entropiclearning.github.io/entlearn/0.1.0/guide/introduction/#literature) and the [tutorial series](https://entropiclearning.github.io/entlearn/0.1.0/tutorials/series/); related methods provide context, not direct evidence for entlearn behaviour. When making an empirical claim, name the method, dataset scope and source.
