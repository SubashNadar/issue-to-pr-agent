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
| 7 | Memory store | Mem0 or Graphiti needs its own storage: a vector store or a graph database. | Project owner | Choose the store and where it runs. | Open |
| 8 | Graphify behaviour | The current notes come from search summaries, not from running the tool. | Project owner | Run it on the reference repository. Confirm the output files and whether incremental updates are supported. | Open |
| 9 | Azure OpenAI details | Which GPT-4 and GPT-5 deployments exist in the region, their token quotas, and the data terms for the resource. | Project owner | Confirm the deployments and quotas. Check Microsoft's current data terms for the chosen resource. | Open |
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

## Closed items

None yet.
