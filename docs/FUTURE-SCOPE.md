# Future Scope

**Audience:** everyone. **Status:** pending items, not part of the MVP.

Each item says what it adds, why it waits, and what it depends on. Items are grouped by theme. Nothing here is scheduled.

## 1. More intake channels

| Item | What it adds | Why it waits | Depends on |
|---|---|---|---|
| Jira intake | Jira tickets create repository issues, with the same allow-list model (account IDs) | One channel is enough to prove the loop | Gmail intake working end to end; Jira webhook and API token |
| Zoho intake | The same, for Zoho Desk or Zoho Projects | Same reason | Intake abstraction shared with Gmail and Jira |
| Jira and Zoho write-back | Summaries posted as comments on tickets | Depends on intake | Approval queue; the relevant write permissions |

## 2. More repository providers

| Item | What it adds | Why it waits | Depends on |
|---|---|---|---|
| GitLab | Issues, merge requests, and webhooks | GitHub is the MVP provider | A provider adapter that matches the GitHub one |
| Bitbucket | Issues, pull requests, and webhooks | Same reason | Same adapter; confirm webhook signing against current docs |
| AWS CodeCommit | Repositories, pull requests, and triggers | Different event model; no issue tracker of its own | Decide the issue source (often Jira or GitHub) |
| Azure DevOps | Work items, repositories, pull requests, and service hooks | Same reason | Same adapter; a scoped personal access token for the project |

The adapter interface is designed so that adding a provider doesn't change the pipeline. Code hosts, trackers, and chat tools are separate ports; see [INTEGRATIONS.md](INTEGRATIONS.md).

| Item | What it adds | Why it waits | Depends on |
|---|---|---|---|
| Asana intake | Asana tasks start the fix loop, with a tag in place of the `agent-fix` label | Same reason as Jira and Zoho | Tracker port; Asana webhook handshake |
| Slack approvals | Approve and reject buttons in a channel | Approval channel not chosen yet (open item 1) | Notifier port; approval service |
| Zoho Cliq approvals | The same flow through a Cliq bot | Same reason | Notifier port |
| Microsoft Teams approvals | The same flow through Adaptive Cards | Same reason | Notifier port |

## 3. Feature requests

Feature requests are a different job. A bug has a failing test to aim for; a feature doesn't.

The planned approach:
- The agent turns the request into a short spec with acceptance criteria.
- A maintainer approves the spec before any code is written. This gate matters most.
- The agent implements against the criteria and writes tests from them.
- The PR is reviewed as a larger change and may need several rounds.

**Depends on:** the bug path working, a way to judge a feature's success, and an approval step for specs.

## 4. Visual evidence in summaries

Screenshots help a reporter see what changed. They are not in the MVP, for three reasons: they need a running app in the sandbox, they can leak sensitive data, and delivery differs by channel.

| Option | How it works | Limits |
|---|---|---|
| Gmail attachment | The screenshot is attached to the reply | Must be redacted first |
| GitHub comment | The image is committed to the `agent/*` branch and linked | Needs a repository write; the image sits in the branch history |
| Playwright capture | Before and after screenshots of the affected page | Web bugs only; needs a runnable app in the sandbox |

**Depends on:** the sandbox running the application, a redaction step, and the approval gate applying to images too.

## 5. Setup experience

| Item | What it adds | Depends on |
|---|---|---|
| VS Code extension | Guided setup: connect GitHub, store keys in the editor's secret store, edit the allow-list, check health | Stable configuration format from the MVP |
| Marketplace publishing | Public listing for the extension | Extension working; publisher account; licence decision |
| Setup test button | Runs the full path on a sandbox repository from the extension | Extension and a sandbox test repository |

## 6. Intake and rules authoring

| Item | What it adds | Depends on |
|---|---|---|
| Langflow intake flows | Visual, editable intake logic | Intake logic stable in code first |
| Advocate-editable rules | Non-engineers edit the rules that decide what counts as a valid report | Rules format that can be reviewed safely |

## 7. Storage and operations

| Item | What it adds | Depends on |
|---|---|---|
| Persistent storage | PostgreSQL for reply limits, job queue, and audit history, replacing in-memory state | MVP working; migration plan |
| Incremental code graph | Update the graph for changed files only | Graphify support for incremental updates, to be confirmed |
| Cost and usage dashboards | Per-issue cost, token use, and rate-limit events | Audit log and metrics in place |
| Multi-repository deployments | One deployment serving several repositories | Per-repository allow-lists and memory |

## 8. Models and data handling

| Item | What it adds | Depends on |
|---|---|---|
| Model provider setting | One configuration for Azure OpenAI, OpenAI, or Anthropic | Model client abstraction |
| Self-hosted model option | Code never leaves the organisation | Hardware and a model with adequate code ability |
| Data-handling note per provider | Plain-language summary of what each provider stores and for how long | Provider terms, checked when the option is added |

## 9. Team integration

| Item | What it adds | Depends on |
|---|---|---|
| CODEOWNERS integration | Route drafts to the code owners automatically | Memory of ownership; repository permission |
| Team notifications | Chat or email digests of pending approvals | Approval queue |

## 10. Trust and safety extensions

| Item | What it adds | Depends on |
|---|---|---|
| Dependency change blocking | Stricter rules for patches that add or change dependencies | Patch review pipeline |
| Second reviewer for risky changes | A second maintainer approval for changes to sensitive paths | Path rules and approval queue |

## Order of work after the MVP

Suggested order, based on value and dependency:

1. Persistent storage, so the MVP's state survives restarts.
2. Model provider setting, so other providers are a configuration change.
3. Jira intake and write-back, the most common second channel.
4. Visual evidence for web bugs.
5. Feature-request path, with the spec gate.
6. VS Code extension and Marketplace publishing.
7. Further providers, in the order users ask for them.

## Jira and GitHub bridge (proposed module)

**Status:** planned. It is currently after the MVP, because the MVP is Gmail intake and GitHub only.

**What it does:** keeps a Jira ticket and a GitHub issue linked and in sync. A ticket created in Jira becomes a GitHub issue, and status and comments flow both ways without duplicates.

**Why it matters:** teams that use both tools currently copy information by hand. The bridge also gives the agent a second intake path, since a Jira ticket can start the same fix loop as an allow-listed email.

**Design:**
- **Inbound:** a Jira webhook, verified by its signature. Only allow-listed Jira account IDs can create work, the same rule as for email and GitHub authors.
- **Outbound:** GitHub events update the Jira ticket: draft PR opened, merged, or closed.
- **Link table:** every pair of Jira key and GitHub issue number is stored once. Redelivered events are ignored by their delivery ID.
- **Loop prevention:** the bridge marks its own writes, and ignores events that it caused. Without this, two-way sync loops.
- **Conflict policy:** the GitHub issue is the source of truth for the fix. Jira holds the request and the status. A conflict is logged and routed to a maintainer, never resolved silently.
- **Writes:** every write to Jira or GitHub follows the approval rules in `BOUNDARIES.md`.

**Measures:**
- duplicate issues created (target: zero)
- sync lag between the two systems (target: under one minute for each event)
- loops detected and stopped (target: zero in a run)
- conflicts routed to a human, with the reason

**Dependencies:** the Jira intake path, the approval service, and the same audit log as the rest of the agent.

**Scope impact:** adding it to the MVP would extend the seven-week plan. The cut list in `PLAN.md` would have to change, most likely by moving the summary write-back to Jira after the MVP.
