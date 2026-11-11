# Reading guide: Recursive SI

[Back to the collection](README.md)

## Identify what changes

Start with the artifact being updated: agent code, a prompt, a skill library, a memory, an evaluator, model weights, or the environment. These changes require different evidence and should not be treated as interchangeable.

[Foundations & surveys](index.html?category=Foundations+%26+surveys#library)

## Follow a short reading route

Begin with the self-evolving agents survey for vocabulary. Then read Darwin Gödel Machine for code evolution, Who Grades the Grader for evaluator drift, WikiSkill for persistent knowledge, and Continual Harness for adaptation during interaction.

[Self-evolving agents survey](https://arxiv.org/abs/2507.21046) · [Core readings](index.html?core=1#library)

## Separate improvement from evaluation

Record who proposes a change, what feedback guides it, and how the candidate is accepted. If the evaluator also evolves, examine the independent evidence used to check it. Higher task scores alone may not establish that evaluation remains reliable.

[Who Grades the Grader](https://arxiv.org/abs/2607.12790) · [Evaluators & feedback](index.html?category=Evaluators+%26+feedback#library)

## Compare systems on common axes

Use the change target, update timing, feedback source, acceptance rule, and persistence across tasks as separate comparison axes. The browser uses ten subject areas; paper, survey, article, book, and tool labels indicate the kind of resource.

[Online adaptation](index.html?category=Online+adaptation#library) · [Memory & skills](index.html?category=Memory+%26+skills#library)

## Inspect evidence and failure modes

Look for held-out evaluation, component ablations, cost accounting, repeated improvement rounds, and state-reset controls. Distinguish results from a paper, an industry account, and a working software repository. A successful update is not by itself evidence of sustained recursive improvement.

[Safety & measurement](index.html?category=Safety+%26+measurement#library) · [Tools & infrastructure](index.html?category=Tools+%26+infrastructure#library)
