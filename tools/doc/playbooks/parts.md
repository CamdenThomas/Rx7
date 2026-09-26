# Playbook: a parts round (D-388, D-390 → D-405)

Choosing a product is money, so it is always his ruling. A round is how the ruling is asked
for.

1. Pick the parts to search: rows whose spec is settled (nothing in their gate is open), plus
   any part whose last pick was vetoed. Read every veto for that part first. His reason
   rules out a class of product, not just the one item. A decision that changes a part's
   premise withdraws its proposed picks in the same pass.
2. For each part, find one **primary** and one **runner-up**. Each gets real listings with
   prices, the numbers that meet the parts row's spec, why, honest drawbacks, a confidence,
   and what must still be confirmed (R11: a fit nobody has measured is `confirm`). Add them to
   `picks`, with the primary `proposed` and the runner-up `reserve`. The app shows every
   `proposed` pick as a question at once; there is nothing else to write.
3. He answers any, some or all, whenever he likes: `yes`, `no` with a reason, or a question.
4. When answers are in the inbox (`kind=pick`), read every one before touching anything.
   Classify each the way the apply playbook does:
   - A **yes** makes the pick `accepted`. The yeses in one pass become one decision naming
     each product, and each parts row is updated (`spec` names the product, the prices,
     `status` `chosen`).
   - A **no** makes it `vetoed`. The runner-up is proposed next unless his reason rules it
     out too; otherwise the search starts again.
   - A **question or an unclear answer** leaves it `proposed`. Answer the question in the
     next suggestion for that part (its `why` or `confirm`), or sharpen the pick.

   His words go in `picks.said`, verbatim, every time. Then delete exactly the inbox rows
   whose verdict and words are saved.
