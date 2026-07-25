# Debugging log

Real issues encountered during development, root causes, and fixes.

---

## 1. Cost Explorer grouping by tag returned empty tag values

What happened: Querying Cost Explorer with GroupBy on the "team" tag returned results, but every group showed as "team$" with no value after the dollar sign, even though the underlying resources were correctly tagged (verified back in Project 1's tagging guardrail).

Root cause: AWS Cost Explorer requires tags to be explicitly activated as "cost allocation tags" before they appear in queryable cost data. This is a separate, manual opt-in step, distinct from simply applying a tag to a resource. Additionally, activation is not retroactive: only cost data recorded after activation includes the tag grouping, with a typical propagation delay of up to 24 hours.

Fix: Activated the team and cost-center tags under Billing and Cost Management > Cost Allocation Tags in the AWS Console. Verified the query logic itself was correct by inspecting the response structure, and proceeded with local test data for downstream development rather than blocking on the propagation delay.

Interview angle: A genuinely non-obvious AWS behavior that most self-taught candidates never encounter, since it only surfaces once you try to query cost data by tag for real. Demonstrates the difference between "the code is wrong" and "the code is correct but the data source has an activation/propagation requirement" — an important distinction in real troubleshooting.
