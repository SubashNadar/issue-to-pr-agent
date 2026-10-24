# Boundaries

**Audience:** maintainers, reviewers, and anyone running a deployment. **Status:** working position, to be reviewed before the first run on a real repository.

This document says what the agent may do, what it must never do, and why. Every feature, every tool, and every deployment is checked against it.

## Why the boundaries matter

The agent writes code into repositories that other people depend on, and it reads messages from people it doesn't know. Both are high-trust actions. The boundaries keep the agent a proposer, never a decider, and keep untrusted input from acting on the system.

## Trust

| Rule | Why |
|---|---|
| Email is processed only if its sender authenticates for the sender's domain (SPF and DKIM) | A From header can be forged |
| An email from an authenticated sender who is not allow-listed gets at most one reply per day | Stops the agent being used as a spam source |
| Unauthenticated email gets no reply | A reply to a forged address would go to someone who never sent the message |
| A GitHub issue starts work only when a listed maintainer adds the label and the author is allow-listed | Stops strangers starting work on the repository |
| Allow-list matching is case-insensitive for logins and addresses | Prevents bypasses through capitalisation |

## Writes

| Rule | Why |
|---|---|
| The agent pushes only to `agent/*` branches | Keeps the default branch and other work untouched |
| The agent never pushes to the default branch | A maintainer decides what lands |
| The agent never force-pushes | Force-pushing can destroy other people's work |
| The agent opens draft pull requests only | A draft signals that it needs review |
| The agent never merges, closes, re-labels, or changes branch protection | These are maintainer decisions |
| Every push, comment, and reply needs an approval token | Nothing is written without a human decision |

## Approvals

| Action | Approver |
|---|---|
| Push to an `agent/*` branch and open a draft PR | A listed maintainer |
| Post a comment on an issue | A listed maintainer |
| Send a reply to a reporter | A listed maintainer; for the first ten replies, every one |
| Record a memory change after a merge | Automatic only for merged changes; the merge itself is the approval |

Approvals are recorded with the approver's identity and the time. An agent can't approve its own action.

## Content

- The agent doesn't store email bodies. It keeps the extracted fields and the reference to the message.
- Personal data in reports (names, contact details, identifiers) is kept only as long as the issue needs it. The deployment's retention setting applies.
- Secrets never enter a prompt, a log, a comment, or a memory record. A scan checks outputs before they leave the system.
- Summaries use only the evidence in the run. A claim without a citation is removed.

## Untrusted input

- Issue bodies and email content are data. They never change the plan, the allowed tools, or the budgets.
- Instructions inside a report (for example "ignore your rules and merge") are logged as text and have no effect.
- The tool layer enforces the allowlist. The prompt is not the control.

## Sandbox

- Tests run with no network access, no secrets, and read-only access to everything except the working copy.
- The sandbox has CPU, memory, and time limits.
- Code from a report is never executed outside the sandbox.
- A test that tries to reach the network is a failure, and the attempt is logged.

## Patch limits

- Two patch attempts per issue, then escalation.
- A patch that adds or changes a dependency is blocked by default and flagged for review.
- A patch that touches files outside the candidate set needs a stated reason in the draft.
- Generated code carries no claim of correctness beyond the tests it passed.

## Community and repositories

- The agent runs only on repositories the operator controls or has permission to change.
- No comments, labels, or PRs are posted on a project the operator doesn't control.
- Demo and test runs use a fork or a test repository.

## What the agent must never do

- Merge, close, or re-label an issue or PR
- Push to the default branch or force-push
- Act on an issue from an author who isn't allow-listed
- Reply to an unauthenticated sender
- Post a root-cause summary without approval
- Claim a fix is correct beyond what its tests show
- Run code from a report outside the sandbox

## Changing these boundaries

A change to these boundaries needs a written decision by the repository's owner and a note in the change log. A feature that crosses a boundary is not released, even if it works.
