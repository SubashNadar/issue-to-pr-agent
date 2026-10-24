# Issue-to-PR Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: planning](https://img.shields.io/badge/status-planning-blue.svg)](docs/PLAN.md)

An open-source agent idea: turn a trusted bug report into a reviewed draft fix, then send the reporter a summary of the root cause, with a screenshot where it helps.

This repository holds the **project idea, walkthrough, and plan** only. No implementation exists yet.

## What the project will do (MVP)

1. A bug report arrives by **Gmail** from a sender on an allow-list.
2. A maintainer adds the `agent-fix` label on a **GitHub** issue.
3. The agent finds the relevant code using memory of past fixes and a code graph.
4. It reproduces the bug with a failing test in a sandbox.
5. It patches the code on a branch and runs the tests.
6. It opens a **draft pull request**. A human reviews and merges.
7. It sends a **root-cause summary**, with citations, back to the reporter and the GitHub issue, once a maintainer approves it.

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

The full scope is in [docs/PITCH.md](docs/PITCH.md). The pending items are in [docs/FUTURE-SCOPE.md](docs/FUTURE-SCOPE.md).

## Documentation

| Document | Audience | What it covers |
|---|---|---|
| [docs/PITCH.md](docs/PITCH.md) | Mentor, stakeholders | The problem, the proposal, MVP scope, risks, and decisions needed |
| [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) | Anyone new to the project | A worked example, step by step, from report to summary |
| [docs/PLAN.md](docs/PLAN.md) | Builders | Phases, milestones, cut list, risks, and definition of done |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture review | Components, protocols, trust model, flows, data, security, deployment, decisions |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Reviewers | Metrics, datasets, targets, and security tests |
| [docs/FUTURE-SCOPE.md](docs/FUTURE-SCOPE.md) | Everyone | Pending items, grouped by theme, with their dependencies |
| [docs/OPEN-ITEMS.md](docs/OPEN-ITEMS.md) | Owner, collaborators | Unresolved decisions and external dependencies, with owners and status |

## Principles

1. **Trust is an allow-list, not a judgement.** Only listed senders can start the agent.
2. **The agent proposes, a human decides.** Draft changes only. Merging, closing, and labelling stay with maintainers.
3. **Every claim has a source.** Root-cause summaries cite a file, line, commit, or test. Uncited claims are removed.
4. **Keys stay with the user.** Credentials live in the user's own deployment, never in a central service.

## Technology

| Technology | Used for |
|---|---|
| **Gmail API** | Reading labelled reports; sending replies and summaries |
| **GitHub API and webhooks** | Triggers, branches, draft PRs, comments |
| **Azure OpenAI** | The model behind reasoning, patching, and summaries |
| **LangGraph** | Orchestration with checkpointed state |
| **A2A** | Communication between specialist agents |
| **MCP** | Governed tool access: repository, docs search, sandbox |
| **LlamaIndex** | Retrieval over code and docs |
| **Mem0** (or Graphiti) | Persistent memory of past fixes and conventions |
| **Graphify** | Code graph of the repository |
| **gRPC** | Streaming sandbox results to the orchestrator |

## Licence

MIT. See [LICENSE](LICENSE).
