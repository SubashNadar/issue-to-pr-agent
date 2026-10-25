# Issue-to-PR Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: planning](https://img.shields.io/badge/status-planning-blue.svg)](docs/PLAN.md)

An open-source agent that turns a trusted bug report into a reviewed draft fix, then sends the reporter a summary of the root cause.

This repository holds the **idea, use cases, plan, and verification approach** only. No implementation exists yet.

## What it does (MVP)

1. A bug report arrives by **Gmail** from a sender on an allow-list, or as a **GitHub** issue from an allow-listed author.
2. A listed maintainer adds the `agent-fix` label.
3. The agent finds the relevant code using memory of past fixes, a code graph, and search.
4. It reproduces the bug with a failing test in a sandbox.
5. It patches the code on an `agent/*` branch and runs the tests.
6. It opens a **draft pull request**. A maintainer reviews and merges.
7. It sends a **root-cause summary**, with citations, to the reporter and the issue, once a maintainer approves it.

The agent never pushes to the default branch and never merges.

## Scope at a glance

| Area | MVP | Future |
|---|---|---|
| Intake channel | Gmail | Jira, Zoho |
| Repository provider | GitHub | GitLab, Bitbucket, AWS CodeCommit, Azure DevOps |
| Model | Azure OpenAI (GPT-4 or GPT-5 deployment, user's own key) | Other providers behind the same setting |
| Work type | Bug reports | Feature requests (with spec approval) |
| Evidence in summary | Text with citations | Screenshots, with redaction |
| Setup | Self-hosted, user's own keys | VS Code extension, Marketplace |

## Documentation

| Document | Audience | What it covers |
|---|---|---|
| [docs/PITCH.md](docs/PITCH.md) | Mentor, stakeholders | The problem, the proposal, MVP scope, roadmap, risks, and decisions needed |
| [docs/USE-CASES.md](docs/USE-CASES.md) | Everyone | Who uses the agent, for what, with diagrams |
| [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) | Anyone new | A worked example, step by step, from report to summary |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture review | Components, protocols, trust model, flows, data, security, deployment |
| [docs/AGENTS-TOOLS-SEARCH.md](docs/AGENTS-TOOLS-SEARCH.md) | Builders, architecture review | Agents, MCP tool catalogue with access matrix, search engine, with diagrams |
| [docs/PLAN.md](docs/PLAN.md) | Builders | Phases, roadmap chart, milestones, cut list, risks, and definition of done |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | Reviewers | Test layers, metrics, datasets, targets, and security tests |
| [docs/DEMO.md](docs/DEMO.md) | Demo owner, reviewers | Demo scenes with expected results, and rehearsal rules |
| [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) | Builders, architecture review | How the agent plugs into any organisation: code host, tracker, and chat adapters, config, and contract tests |
| [docs/BOUNDARIES.md](docs/BOUNDARIES.md) | Maintainers, reviewers | What the agent may and must never do, and why |
| [docs/FUTURE-SCOPE.md](docs/FUTURE-SCOPE.md) | Everyone | Pending items, grouped by theme, with their dependencies |
| [docs/OPEN-ITEMS.md](docs/OPEN-ITEMS.md) | Owner, collaborators | Unresolved decisions and external dependencies |

## Principles

1. **Trust is an allow-list, not a judgement.** Only listed senders and authors can start the agent.
2. **The agent proposes, a human decides.** Draft changes only. Merging, closing, and labelling stay with maintainers.
3. **Every claim has a source.** Root-cause summaries cite a file, line, commit, or test. Uncited claims are removed.
4. **Keys stay with the user.** Credentials live in the user's own deployment, never in a central service.

## Technology

| Technology | Used for |
|---|---|
| **Gmail API** | Reading labelled reports; sending replies and summaries |
| **GitHub API and webhooks** | Triggers, branches, draft PRs, comments |
| **Azure OpenAI** | The model behind extraction, test writing, patching, and summaries |
| **LangGraph** | Orchestration with checkpointed state |
| **A2A** | Communication between specialist agents |
| **MCP** | Governed tool access: email, repository, docs, code, sandbox, memory, approvals |
| **LlamaIndex** | Retrieval over code, docs, and past fixes |
| **Mem0** (or Graphiti) | Persistent memory of past fixes and conventions |
| **Graphify** | Code graph of the repository |
| **gRPC** | Streaming sandbox results to the orchestrator |
| **OpenTelemetry and Langfuse** | Traces, model-call records, cost |

## Licence

MIT. See [LICENSE](LICENSE).
