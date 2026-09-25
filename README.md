# entlearn skills

Agent skills for researchers using [entlearn](https://github.com/EntropicLearning/entlearn). The collection helps an agent fit, tune, inspect, debug and interpret entropy-optimal network (EON) experiments while leaving ordinary Python, machine-learning and scikit-learn practice to existing tools.

## Skills

| Skill | Responsibility |
| --- | --- |
| `using-entlearn` | Choose the public adapter, design a first model, fit it and expose the right next step. |
| `tuning-entlearn` | Tune supported EON choices and compare initialisations without leaking validation information. |
| `interpreting-entlearn` | Interpret fitted affiliations, weights, dimensions, reconstruction and prediction outputs within their stated limits. |
| `debugging-entlearn` | Diagnose fitting, prediction, data-staging and numerical failures. |
| `using-entlearn-advanced` | Work directly with `Network`, tensor inputs, Network-native persistence or continuation, retained state and other lower-level controls. |

Install the five skills together. The skills hold workflows, decision gates and completion
checks; the versioned [entlearn documentation](https://entropiclearning.github.io/entlearn/0.1.0/)
owns the concepts, guidance and references, and each skill links to it.

## Installation

Install the collection into the current project (the `npx skills` default):

```bash
npx skills add EntropicLearning/entlearn_skills
```

To make it available across projects instead:

```bash
npx skills add EntropicLearning/entlearn_skills --global
```

Use `npx skills add EntropicLearning/entlearn_skills --list` to inspect the skills before
installation.

## Compatibility

Releases use tags such as `entlearn-v0.1.0` to identify the entlearn public API and doc-site
version they target. Install a compatible tagged release when reproducibility matters.
Skills inspect the installed package and version rather than assuming that the newest API
is present.

## Authority

For behaviour, the collection follows the matching public entlearn API and source first, then public documentation and examples, skill recommendations, and finally research papers. Papers motivate and contextualise methods; they do not override package behaviour. The papers are listed in the Literature section of the [entlearn documentation](https://entropiclearning.github.io/entlearn/0.1.0/guide/introduction/#literature).

## Release checklist

Before publishing a compatibility tag:

1. confirm that the matching entlearn release's CI and documentation build are green;
2. reconcile changed guidance with that release's public documentation and tutorials;
3. run `python3 scripts/check_skills.py --site-dir <built site> --docs-version <mike version>`
   against the release's built doc site, so every doc link is checked;
4. verify `npx skills add EntropicLearning/entlearn_skills --list` and a temporary
   project-local installation.

The entlearn repository owns package runtime testing. This repository checks the skill structure and release-specific guidance rather than duplicating that test suite.

## Licence

MIT. See [LICENSE](LICENSE).
