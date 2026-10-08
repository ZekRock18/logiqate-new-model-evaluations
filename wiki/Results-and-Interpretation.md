# Results and Interpretation

The run completed all 1,035 expected evaluation units. The zero-shot control
scored 62/135 overall and 25/75 on the obfuscated cells matched to the three
assigned experiments.

Key observations:

- Obfuscated-to-Obfuscated and Base-to-Obfuscated paired few-shot each scored 26/75 on the assigned obfuscated cells.
- Analogical prompting scored 30/75 on those cells.
- Chain of Thought reached 9/15 on obfuscated FOL.
- Structured Decomposition, Chain of Thought and Self-Consistency each reached 9/15 on Blood Relation L1.
- No method exceeded the 6/15 zero-shot control on Blood Relation L2.
- Explicit Task Instructions reached 5/15 on obfuscated Number Series.
- Self-Consistency reached 11/15 on obfuscated Direction Sense.
- CoVe changed 18 answers, correcting 1 and harming 11.

These are 15-item-per-task pilot estimates. Raw counts should accompany
percentages, and small differences should not be treated as stable effects.

See the [full aggregate report](../experiments/common/results/REPORT.md) and
[machine-readable tables](../experiments/common/results/).
