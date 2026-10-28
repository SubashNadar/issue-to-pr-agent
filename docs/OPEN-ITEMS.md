# Open Items

**Audience:** project owner, collaborators, and reviewers. **Status:** all items open unless marked closed.

Each item says what is unresolved, why it matters, who can close it, and what decision is needed. Items are grouped by when they must be closed. Close an item by changing its status and recording the decision in the document it affects.

## Before Phase 1 (trust layer and intake)

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 1 | Approval mechanism | The safety claim depends on a maintainer approving pushes, draft PRs, and summaries. The docs don't say how that approval happens. | Project owner | Pick the channel: a GitHub comment command, a label, or another route. Define who may approve and how it is recorded. | Open |
| 2 | Reference repository | Its language and test runner decide the sandbox design and whether seeded bugs are practical. | Project owner, with the repository's maintainers | Choose the repository and confirm it meets the criteria in [PLAN.md](PLAN.md). | Open |
| 3 | Sandbox technology | The docs require no network and no secrets, but not how that is enforced. | Project owner | Choose the runtime (for example Docker, or a microVM) and how network and secret isolation is checked. | Open |
| 4 | Webhook hosting | GitHub needs a public HTTPS endpoint. The plan doesn't name a host. | Project owner | Choose where the receiver runs for the reference deployment, and how it is secured. | Open |
| 5 | Gmail OAuth route | Apps in Google's "Testing" status typically have refresh tokens that expire after about seven days, so a demo may need re-authorising weekly. The Gmail read scope is restricted, so distributing a shared app would need Google's verification process. Verify both points against current Google documentation. | Project owner | Decide the route: each deployment uses its own Google Cloud project, or one shared app. Confirm the token lifetime and verification requirements. | Open |
| 6 | Langflow's role | [ARCHITECTURE.md](ARCHITECTURE.md) has Langflow intake flows. [PLAN.md](PLAN.md) uses a Python Gmail connector. | Project owner | Choose one. Update the other document to match. | Open |

## Before Phase 2 (fix loop)

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 7 | Memory store | Mem0 or Graphiti needs its own storage. Decided 28 Oct 2026: LlamaIndex `fixes` and `conventions` collections in pgvector, as in [REPO-MEMORY.md](REPO-MEMORY.md). | Project owner | None. | Closed |
| 8 | Graphify behaviour | The current notes come from search summaries, not from running the tool. | Project owner | Run it on the reference repository. Confirm the output files and whether incremental updates are supported. | Open |
| 9 | Azure OpenAI details | Deployments created 28 Oct 2026: `gpt-5.4-nano`, `gpt-5.4`, `text-embedding-3-large`, on a personal subscription. Quotas, supported parameters, content filters, embedding dimensions, and the data terms are not yet checked. | Project owner | Run the week-1 checks in [AZURE-SETUP.md](AZURE-SETUP.md). | Partly done |
| 10 | Seeded bugs | None exist yet. The evaluation needs ground-truth bugs, each with a failing test. | Project owner | Decide how many bugs, where they come from, and who reviews them. | Open |
| 11 | Dependency versions | A2A is still changing. | Project owner | Pin the A2A SDK and LangGraph versions at the start of the build. | Open |

## Housekeeping (can wait, but before any code lands)

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 12 | Contribution guide and security policy | The definition of done requires both. The repository has neither yet. | Project owner | Write `CONTRIBUTING.md` and `SECURITY.md`. | Open |
| 13 | `.gitignore` | It was removed with the code. It must return before any secrets or local files can appear in the repo. | Project owner | Restore it with entries for secrets, local config, and runtime data. | Open |
| 14 | Audit log retention | The docs state 90-day retention, but nothing enforces it. | Project owner | Decide how retention is enforced, and who may read the log. | Open |

## Capacity and timeline

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 15 | Hours per week | The plan is seven weeks at full pace. The project owner works full-time, so the real timeline depends on available hours. | Project owner | Confirm weekly hours and a target date. Adjust the cut list in [PLAN.md](PLAN.md) to match. | Open |

## External dependencies

These need a party outside the project to act.

| # | Item | Owner | Needed for | Status |
|---|---|---|---|---|
| 16 | Maintainer approval for using the reference repository | The repository's maintainers | Phase 0 | Open |
| 17 | Azure quota and deployment access | Azure subscription owner | Phase 0 and Phase 2 | Open |
| 18 | Google Cloud project and OAuth client | Project owner | Phase 1 | Open |
| 19 | Google verification (only if the app is shared) | Project owner, with Google | Any shared release | Open |

## Added: integrations

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 22 | MVP intake for the NIIT capstone | Organisations mostly file bugs in a tracker, not by email. Jira intake also proves the CodeHost and Tracker ports are separate, which matters for CodeCommit. Swapping it for Gmail removes the OAuth items (5, 18, 19). | Project owner | Decided 28 Oct 2026: phase 1 intake is a Langflow chat box and the code is a local git repository ([CHAT-AND-LOCAL-MODE.md](CHAT-AND-LOCAL-MODE.md)). Jira and Gmail move to phase 2. | Closed |
| 23 | Approval channel through the Notifier port | Item 1 needs a channel. A Slack button gives the demo a visible human decision. | Project owner | Choose a GitHub comment command, a label, or Slack (or Zoho Cliq). | Open |
| 24 | Structured data for the capstone rubric | The NIIT rubric gives 20% to retrieval and data integration, including routing between RAG, SQL, and hybrid. The task and audit store in PostgreSQL can answer SQL questions such as fixes merged per project and cost per issue. | Project owner | Confirm the router and the SQL questions it must answer, and add them to [VERIFICATION.md](VERIFICATION.md). | Open |

## Closed items

None yet.

## Added: reference repository and external servers

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 16 | Reference repository | Chooses the codebase the whole evaluation runs on | Project owner | Pick attrs, typer, or click after timing the test suites. | Open |
| 17 | GitHub MCP server | Its repository, licence, and scopes determine whether it can be the base for `provider-mcp` | Project owner | Confirm the repository and scopes; decide whether to build on it. | Open |
| 18 | Playwright and Context7 publishers | Their use is planned, and their publishers aren't fully confirmed | Project owner | Confirm each publisher and licence before use. | Open |

## Added: Jira and GitHub bridge

| # | Item | Why it matters | Owner | Decision needed | Status |
|---|---|---|---|---|---|
| 19 | Bridge in or out of the MVP | The MVP is Gmail and GitHub only. Adding the bridge extends the schedule. | Project owner | Keep the bridge after the MVP, or move it in and cut something else. | Open |
| 20 | Jira account and permissions | The bridge needs a Jira service account with the narrowest permissions that work | Project owner | Confirm the Jira site, the service account, and the scopes. | Open |
| 21 | Conflict owner | When Jira and GitHub disagree, someone must decide | Project owner | Name the maintainer who receives conflict reports. | Open |
