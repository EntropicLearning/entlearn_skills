---
name: tuning-entlearn
description: Tune entlearn hyperparameters, search ranges, multiple initialisations, model selection, calibration, depth, manifold inputs, iterative prediction, or unexpectedly uncompetitive performance. Use for estimator-wrapped searches; route direct Network optimisation to using-entlearn-advanced.
---

# Tune entlearn

This skill owns the task of selecting settings for the scikit-learn adapters. It holds
the workflow; the entlearn documentation holds the facts, including the
[glossary](https://entropiclearning.github.io/entlearn/0.1.0/concepts/glossary/), the
[concepts](https://entropiclearning.github.io/entlearn/0.1.0/concepts/) and
[suitability and scaling](https://entropiclearning.github.io/entlearn/0.1.0/guide/suitability/).
Links point at the documentation for entlearn 0.1.0, this release's compatibility tag, and
[`llms.txt`](https://entropiclearning.github.io/entlearn/0.1.0/llms.txt) lists every page as
Markdown. When the installed entlearn version differs, replace `0.1.0` in each link with the
installed version and follow that version's pages instead.

## 1. Establish the decision

Identify the scoring rule, desired rigour, and available compute from the existing
experiment. Ask about rigour or compute only when the prompt and environment do not
settle them.

A typical starting point is to fit one representative shallow, standard-input candidate and time it. Include
preprocessing and all initialisations in the measurement. Estimate the proposed search
cost as candidates × folds × initialisations × approximate fit cost, allowing for the
final refit.

**Complete when:** the scorer, split policy, rigour, compute ceiling, and approximate
fit cost are explicit.

## 2. Build a coarse joint search

Read [choosing search ranges](https://entropiclearning.github.io/entlearn/0.1.0/guide/model_selection/#choosing-search-ranges)
before choosing parameters or ranges.

Start with a shallow standard input unless known problem structure indicates a manifold input block,
or depth. Jointly vary the core structural parameters, temperatures and coupling
strength, and treat the coupling as a hyperparameter: sweep M against S. Learn the
feature and instance weights by default, with finite `epsilon_D` and `epsilon_T`. Decide
deliberately whether either should not be learned, and how supplied `sample_weight`
should interact with `epsilon_T`
([a first experiment](https://entropiclearning.github.io/entlearn/0.1.0/guide/hyperparameters/#a-first-experiment),
[sample and class weights](https://entropiclearning.github.io/entlearn/0.1.0/guide/estimators/#sample-and-class-weights)).

Use the fitted adapter with `GridSearchCV` or `RandomizedSearchCV`. `OptunaSearchCV`
([optional Optuna backend](https://entropiclearning.github.io/entlearn/0.1.0/guide/model_selection/#optional-optuna-backend))
and other search objects that wrap the estimator are also valid, but adding one changes project dependencies: obtain user approval
before installation. Route optimisation written directly around `Network` to
`using-entlearn-advanced`.

**Complete when:** the active space searches structure, temperatures and coupling together,
fits the compute ceiling, and every numerical bound has evidence or is labelled as a
pilot bound.

## 3. Resolve initialisation variability

Assess more than one initialisation for every competitive region. During the coarse
stage, spend a small common allocation across candidates. Allocate more
initialisations to promising regions, then compare distributions or stability
summaries rather than only the single best run.

EON is unusually sensitive to hyperparameters and initial state. Treat one poor
configuration as evidence about that configuration, not evidence that EON is
unsuitable for the problem. Choose the initialisation-selection splitter deliberately, apart
from the search's own
([select an initialisation for one recipe](https://entropiclearning.github.io/entlearn/0.1.0/guide/model_selection/#select-an-initialisation-for-one-recipe)).

**Complete when:** more than one initialisation has been assessed for competitive
configurations and stability meets the stated rigour.

## 4. Refine multiple regions

Inspect rankings, score dispersion, failures and runtime. For every searched parameter:

- flag best candidates on a lower or upper boundary of the search box, and compare
  their score uncertainty with adjacent candidates;
- narrow ranges only after checking both boundaries; expand a boundary when the winner
  presses against it and the direction is scientifically and numerically credible and
  affordable;
- treat repeated convergence warnings or extreme runtimes as diagnostics, not
  candidates silently discarded; a loss-increase warning invalidates the fit, so invoke
  `debugging-entlearn`;
- distinguish training–validation gaps from initialisation dispersion;
- verify that the search object optimises the intended scorer and direction.

A flat surface can justify stopping. A boundary winner, unstable ranking, or isolated
good seed cannot. Refine more than one competitive region when results do not clearly
separate them.

Add complexity one question at a time:

- add depth when shallow capacity is a demonstrated limitation;
- compare a manifold input when local low-dimensional geometry is plausible;
- compare the fitted
  [classification calibration](https://entropiclearning.github.io/entlearn/0.1.0/guide/hyperparameters/#classification-calibration)
  against alternatives only with a proper probabilistic scorer, when probability quality is
  the goal;
- compare arithmetic and geometric read-outs where the coupling allows, particularly when depth is being added;
- compare iterative prediction as a refinement on the default single pass.

**Complete when:** competitive regions have been refined and each extra mechanism has
a recorded justification and comparison.

## 5. Select and record

Refit according to the chosen search object's public contract. Record active and
discarded ranges, budget, folds, scorer, initialisation allocation, failed candidates,
selection rule, and held-out result. Preserve uncertainty when candidates are
practically tied.

**Complete when:** a competitive model is selected, or the search supplies credible
evidence that further tuning is unlikely to alter the scientific conclusion; the
ranges, budget, scoring, selection, and stability evidence are reproducible.
