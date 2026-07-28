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

## 4. AWS API calls failed with SignatureDoesNotMatch due to WSL clock drift

What happened: aws sts get-caller-identity and boto3 EC2 calls failed with SignatureDoesNotMatch, reporting the request signature's timestamp was more than 15 minutes outside AWS's accepted window.

Root cause: WSL's system clock had drifted nearly 59 minutes behind real time. AWS signs and validates every API request using a timestamp, and rejects requests where the client's clock has drifted too far from AWS's own time, as a security measure against replay attacks. This is a known WSL behavior, the virtual machine's clock can fall out of sync with the Windows host, particularly after the host sleeps or hibernates.

Fix: Installed ntpsec-ntpdate (the current Ubuntu 26.04 replacement for the deprecated ntpdate package) and ran ntpdate against pool.ntp.org to force an immediate clock correction, confirmed by the reported "time stepped by 3542 seconds" message.

Interview angle: A genuinely non-obvious class of bug, since the actual credentials and code were correct the whole time. Demonstrates reading an error message precisely rather than assuming "credentials are wrong" from a surface-level glance, the specific wording (signature and timestamp, not permissions) was the clue pointing to a clock issue rather than an auth issue.

## 5. Waste detection successfully identified a real idle resource

Note: detect_waste.py was run against the real, live EC2 instance from Project 1 rather than simulated data. It correctly identified the instance as a waste candidate, with 0.15 percent average CPU utilization over 7 days, since the instance has been idle since Project 1's build sessions concluded. This is a genuine, live validation of the detection logic against real production-style data, and a concrete real-world example of the exact problem this project is designed to catch.

## 6. Recurring WSL clock drift caused repeated AuthFailure errors

What happened: AuthFailure and SignatureDoesNotMatch errors recurred multiple times in one session, even after an initial manual ntpdate fix, because WSL's clock drifted again by several minutes within the same working session.

Root cause: A single manual time correction only fixes drift at that instant, it does not prevent the clock from drifting again. WSL's virtual clock is known to drift from the Windows host clock over time without an active, continuously-running sync service.

Fix: Installed and enabled ntpsec as a persistent background service (systemctl enable and start), rather than relying on one-off manual corrections. This keeps the clock continuously synchronized going forward instead of requiring repeated manual intervention.

Interview angle: A good example of the difference between a one-time fix and a durable fix, treating the symptom once versus addressing the actual recurring cause. The same AuthFailure symptom can have multiple underlying triggers across a single session, and reappearing errors after a fix is itself a diagnostic signal worth paying attention to.

## 7. Least-privilege IAM identity validated against real AWS calls

Note: Created a dedicated finops-readonly IAM user scoped to only ce:GetCostAndUsage, ec2:DescribeInstances, cloudwatch:GetMetricStatistics, and s3:PutObject restricted to the single dashboard bucket. Verified by running detect_waste.py under this identity via AWS_PROFILE, confirming it correctly authenticates and returns the same valid result as the broader admin identity, proving the narrower policy grants exactly what the code requires and nothing more.
