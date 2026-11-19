Discourse participation model

Final documents
  Participation_Model_Fitted.docx
  Participation_Model_Fitted.pdf

Project files
  scripts/fit_participation.py   Fit the three participation models and account holdouts.
  scripts/draw_figures.py       Generate the two English figures as PNG and SVG.
  scripts/build_document.py     Build the Word/PDF with embedded figures.
  data/comments_metadata.csv   Original extracted comment metadata and source links.
  data/participation_transitions.csv   Derived post-entry account-days.
  data/participation_model_fit.json    Model estimates and fit diagnostics.
  source/document.txt          Editable text used to build the final documents.
  figures/                    Two current figures, in PNG and editable SVG formats.

Rebuild from this folder (Python 3; dependencies in requirements.txt)
  python3 scripts/fit_participation.py
  python3 scripts/draw_figures.py
  python3 scripts/build_document.py

Scripts resolve paths relative to the project, so they also work from another
working directory. Plotting caches go to the system temporary directory. Builds
do not create preview images, older documents, or a duplicate research ZIP.
For a theory-only diagram revision, use draw_figures.py --process-only to keep
the empirical plot unchanged, then rerun build_document.py.

Model scope
The document separates an unestimated channel-choice mechanism from the fitted
public-return process. In the first, expected benefit minus the opportunity
cost of time determines a noisy choice among public advice, private advice and
other work. Expertise could increase costs, benefits or efficiency, so its
effect on public participation is ambiguous. This mechanism is motivated by
Kirchner's Via productiva (2022):
https://universalprior.substack.com/p/via-productiva
Belief entrenchment is also an unestimated extension. Neither extension changes
the three fitted specifications or their saved estimates.

Data scope
The input CSV contains 60 unique comments from two LessWrong threads. The fitted
model selects the 53 comments labeled lw_main, from 27 accounts in the release
thread for Alignment Faking in Large Language Models:
https://www.lesswrong.com/posts/njAZwT8nkHnjipJku/alignment-faking-in-large-language-models

Window: 2024-12-18 00:00 UTC inclusive to 2025-01-02 00:00 UTC exclusive.
Snapshot: 2026-11-19. The model conditions on each account's first contribution;
352 subsequent account-days include seven active days. It does not estimate
silent readers' initial entry, opportunity costs, private advice or private
beliefs. Never-posting experts are outside the sample. The lag model has one unstable
account holdout. The estimated model describes conditional participation; it
does not establish a causal effect of incentives or belief entrenchment.

Author's online working documents (access may be required)
Model: https://chatgpt.com/space/page_ad54df9105a08191ab477c5a41c12da9
Research notes: https://chatgpt.com/space/page_9ba53381ab408191ad16727d728aaa07
