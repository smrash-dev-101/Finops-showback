# Debugging log

Real issues encountered during development, root causes, and fixes.

---

## 1. Cost Explorer grouping by tag returned empty tag values

What happened: Querying Cost Explorer with GroupBy on the "team" tag returned results, but every group showed as "team$" with no value after the dollar sign, even though the underlying resources were correctly tagged (verified back in Project 1's tagging guardrail).

Root cause: AWS Cost Explorer requires tags to be explicitly activated as "cost allocation tags" before they appear in queryable cost data. This is a separate, manual opt-in step, distinct from simply applying a tag to a resource. Additionally, activation is not retroactive: only cost data recorded after activation includes the tag grouping, with a typical propagation delay of up to 24 hours.

Fix: Activated the team and cost-center tags under Billing and Cost Management > Cost Allocation Tags in the AWS Console. Verified the query logic itself was correct by inspecting the response structure, and proceeded with local test data for downstream development rather than blocking on the propagation delay.

Interview angle: A genuinely non-obvious AWS behavior that most self-taught candidates never encounter, since it only surfaces once you try to query cost data by tag for real. Demonstrates the difference between "the code is wrong" and "the code is correct but the data source has an activation/propagation requirement" — an important distinction in real troubleshooting.

## 2. Anomaly detection flagged a normal day as an anomaly on first run

What happened: Running the z-score based anomaly detector against freshly simulated data flagged platform-team as an anomaly, even though the underlying data was pure random variation with no deliberately injected spike.

Root cause: This is not a bug. A z-score threshold of 2.0 standard deviations will, by the mathematical nature of a normal distribution, flag approximately 5 percent of genuinely normal observations as anomalous purely by chance. This is the expected false-positive rate for that threshold, not a flaw in the detection logic.

Resolution: None needed, this is correct behavior. Documented explicitly so the tradeoff is understood rather than mistaken for a defect: a lower threshold catches more real anomalies but produces more false positives, a higher threshold produces fewer false positives but risks missing real anomalies. The threshold of 2.0 was chosen as a reasonable starting point, adjustable based on how noisy real alerting proves to be in practice.

Interview angle: Demonstrates statistical literacy around anomaly detection specifically the false-positive/false-negative tradeoff inherent to any threshold-based alerting system, rather than presenting anomaly detection as something that can be made perfectly accurate.

## 3. Terraform state for dashboard bucket kept local, not remote

Note: Unlike Project 1's IDP platform, this project's Terraform state is kept as a local file rather than a remote S3 backend. This was a deliberate scope decision: the dashboard bucket is a single, low-stakes resource, and setting up a full remote-state backend (S3 + DynamoDB locking) for one small bucket was judged not worth the added complexity for this project's scope. The tradeoff: if the local state file is lost, Terraform loses track of these resources, though they would continue to exist and function in AWS. Acceptable risk for this scope, would not be acceptable for a team-shared or production-critical resource.
