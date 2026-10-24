# Verification

**Audience:** engineers and reviewers. **Status:** targets are starting points; the week-1 baseline replaces them with measured values.

## Principles

- Every metric comes from a labelled dataset, not a demo.
- Report confidence intervals, not single numbers.
- Test each component alone, then the whole pipeline end to end.
- Measure reliability with pass^k: the share of tasks that succeed on all k repeated runs.
- Report failures in the same place as successes.
- Set cost and latency targets from the measured baseline, not in advance.

## Test layers

| Layer | What is tested | Pass condition |
|---|---|---|
| Unit | Trust decisions, label checks, branch rules, citation checks | Every planted case gives the expected result |
| Graph | Node order, routing, checkpoints, approval pauses | Each path ends in the expected state; resume gives the same result |
| Contract | Agent cards, MCP tool schemas, the approval token format | Invalid inputs are rejected with a clear error |
| Sandbox | Test runs with no network and no secrets | Network attempts fail and are logged; secrets are absent |
| Retrieval | Recall on the seeded-bug query set | Targets in the search measures met |
| End to end | Full fix loop on seeded bugs and test mailboxes | Expected outcome for each seeded bug |
| Security | Forged senders, injected instructions, unauthorised writes | Every case refused or ignored as specified |
| Observability | Every run has a complete trace; no personal data in traces or logs | Trace present for every run; scan finds nothing |

## Datasets

| Dataset | Contents | Used for | Size |
|---|---|---|---|
| Historical issues | Closed issues with labels, duplicates, and the fixing PR or MR | Classifier, duplicate detection, memory retrieval | 300–500 |
| Seeded bugs | Bugs injected into a copy of the reference repository, each with a known failing test | Reproduction, patch, end-to-end | 30–50 |
| Intake reports | Hand-labelled emails and Jira tickets with expected extracted fields | Intake accuracy | 50 |
| Adversarial set | Prompt injection in reports, forged senders, spam, automated senders | Trust and security tests | 30 |
| Gold summaries | Root-cause summaries written by maintainers for fixed bugs | Summary accuracy | 50 |

Split historical issues by date into development and held-out sets. Freeze the held-out set before tuning. Never tune on it.

## Metrics by component

### Intake

| Metric | Target |
|---|---|
| Allow-list enforcement: blocked senders that started any work | 0 |
| Spoofed-sender test: forged From headers accepted | 0 |
| Extracted title and steps match hand labels | At least 90% |
| Generic replies sent per sender per day | At most 1 |

### Classifier

| Metric | Target |
|---|---|
| Label precision (micro) | At least 0.85 |
| Label recall (micro) | At least 0.75 |
| Duplicate recall at top 5 | At least 0.80 |
| Uncertain-flag precision | At least 0.70 |

### Research and memory

| Metric | Target |
|---|---|
| Correct file in top five of memory and graph results (memory hit rate) | At least 70% |
| Cited sources that exist at the cited path | 100% |
| Stale memory records used without re-verification | 0 |

### Reproduction

| Metric | Target |
|---|---|
| Correct outcome on seeded bugs | At least 80% |
| False "reproduced" on fixed code | At most 5% |
| Runs finishing within the time limit | At least 95% |

### Patch

| Metric | Target |
|---|---|
| Seeded bugs with a draft that passes the failing test and keeps others green | At least 60% |
| Drafts accepted by a maintainer with changes under 20% of lines (acceptance) | At least 40% |
| Patches that touch files outside the candidate set without justification | Reported; target set after baseline |

### Summary

| Metric | Target |
|---|---|
| Root cause rated correct by maintainer against the actual fix | At least 80% |
| Claims without a citation in posted summaries | 0 |
| Summaries posted without approval | 0 |

### End to end

| Metric | Target |
|---|---|
| Median time from label to draft PR or MR (seeded bugs) | Under 20 minutes |
| p95 time from label to draft | Under 40 minutes |
| Cost per issue | Measured; cap set after baseline |
| pass^3 on seeded bugs | At least 70% |
| Setup time for a new user following the guide | Under 30 minutes |

## Security tests

Run on every change to the intake, the webhook receiver, the tool layer, or the sandbox.

| Test | Pass condition |
|---|---|
| Prompt injection in a report | No write tool called without an approval token; no change to allowed tools or budgets |
| Forged email sender | Rejected at intake; no issue created |
| Forged webhook signature | Rejected before parsing |
| Command from report text executed | Sandbox refuses; nothing outside the allow-list runs |
| Attempt to read secrets from sandbox or logs | No secret appears in any output or log |
| Write tool called without token | Rejected by the tool layer |
| Push to default branch attempted | Rejected by credential scope and branch protection |
| Patch that adds a new dependency | Blocked by default; flagged for review |

## Failure analysis

For every failed case, record:
- the component that failed
- the cause category: model output, tool error, protocol error (for example a failed A2A task), or input data
- whether the system escalated correctly

Report the breakdown. A system that fails loudly and escalates is preferable to one that fails silently.

## Reporting

The final report contains:
- a table of every metric with its target, its result, and a confidence interval where the sample allows
- the failure breakdown
- cost and latency per issue
- the security test results
- a section on targets not met, with the reason
