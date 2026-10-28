# Plan

**Audience:** builders and collaborators. **Status:** planned, not started. Restructured 28 Oct 2026 into demoable releases.

The MVP is the scope in [PITCH.md](PITCH.md). This plan says how to build it, in what order, and what to cut if time runs short. Pending items beyond the MVP are in [FUTURE-SCOPE.md](FUTURE-SCOPE.md).

## How this plan is shaped

Each release is a **thin, working slice that can be demoed on its own**. Nothing is built "for later": every release ends with a short demo on the fork, and each one adds to the last. If time runs out after any release, there is still a complete, honest demo to present.

Phase 1 (the capstone) is **Python repositories, reported through a Langflow chat box, fixed in a local git repository**. Java, C#, other code hosts, and other trackers are phase 2. The design already supports them (see [REPO-MEMORY.md](REPO-MEMORY.md) and [INTEGRATIONS.md](INTEGRATIONS.md)), so the viva line is: "built for many languages, hosts and trackers; phase 1 proves it on Python, a local repo and a chat box."

## Decided before starting

- Phase 1 scope: Python repositories on the owner's machine. Bugs are reported in a **Langflow chat box**, and the agent works on a **local git** repository through worktrees. See [CHAT-AND-LOCAL-MODE.md](CHAT-AND-LOCAL-MODE.md). No Jira is needed.
- GitHub draft PRs are optional (R5): push the repo to a private GitHub repo and switch the CodeHost adapter.
- Model: Azure OpenAI on the owner's personal subscription: `gpt-5.4-nano`, `gpt-5.4`, `text-embedding-3-large`. See [AZURE-SETUP.md](AZURE-SETUP.md).
- Memory: LlamaIndex collections in pgvector. See [REPO-MEMORY.md](REPO-MEMORY.md).
- Agents run as LangGraph sub-graphs in one process. Splitting them into A2A services is phase 2.
- A per-issue token cap protects against runaway loops.
- Forks are allowed. Licence: MIT.

## Roadmap

```mermaid
gantt
  title Phase 1 releases (full-time assumption; adjust to available hours)
  dateFormat YYYY-MM-DD
  section Releases
  R0 Foundations                     :r0, 2026-11-02, 7d
  R1 Chat to fix branch              :r1, after r0, 14d
  R2 Trust, critic, summary          :r2, after r1, 7d
  R3 Memory and routing              :r3, after r2, 7d
  R4 Evaluation and SLOs             :r4, after r3, 7d
  R5 Demo polish                     :r5, after r4, 7d
  section Demo checkpoints
  One seeded bug fixed end to end    :milestone, m1, after r1, 0d
  Refusals and approvals shown       :milestone, m2, after r2, 0d
  SLO report ready                   :milestone, m3, after r4, 0d
  Final demo rehearsed               :milestone, m4, after r5, 0d
```

Seven weeks at full time. With fewer hours, the dates stretch and the cut list applies sooner.

## Releases

| Release | Weeks | What works at the end | Demo you can give | Rubric areas shown |
|---|---|---|---|---|
| R0 Foundations | 1 | Docker Compose (Postgres with pgvector, Langfuse, Langflow), Azure smoke tests, FastAPI `/health`, local repo with 10 seeded bugs | One model call traced in Langfuse; the seeded-bug list | Backend, observability |
| R1 Chat to fix branch | 2–3 | Chat message → Langflow extract → `POST /runs` → classify → research → failing test → patch → `approve 12` in chat → `agent/issue-n` branch + patch | One seeded bug fixed end to end from the chat box | Architecture, tools, multi-agent, retrieval (basic) |
| R2 Trust, critic, summary | 4 | Refusal paths, audit log, critic and confidence, escalation, cited summary with approval | Scenes 4, 6, 7, 8: refusals, "won't answer", human gates | Human-in-the-loop, guardrails |
| R3 Memory and routing | 5 | Refresh on merge and `/agent reindex`, `fixes` collection, SQL tables, RAG/SQL/hybrid router | Merge a PR and watch memory update; one RAG, one SQL and one hybrid question | Retrieval and data (20%) |
| R4 Evaluation and SLOs | 6 | 50 golden queries, 10 seeded bugs run, red-team set, small-to-strong model escalation, SLO report | SLO dashboard with every target met or explained | SLO and evaluation |
| R5 Demo polish | 7 | React UI (runs, approvals, repos), optional GitHub draft PRs and Slack approvals, guide, rehearsal | The full 5-minute demo in [DEMO.md](DEMO.md) | Documentation and defence |

### R0: Foundations (week 1)

- Clone the reference repository (see below) to your machine and seed 10 Python bugs on a branch, each with a failing test and a known fixing file. Your own Python project also works, as long as it isn't an employer's code.
- `docker-compose.yml`: PostgreSQL with pgvector, Langfuse, Langflow, the API.
- Azure checks from [AZURE-SETUP.md](AZURE-SETUP.md): smoke tests, supported parameters, quota.
- FastAPI skeleton, Pydantic settings, `.env.example`, pytest running in CI.
- Register the local repo (`itp repo add --path ...`).

**Demo:** a traced model call in Langfuse, and the seeded bugs listed with their failing tests.

### R1: Chat to fix branch (weeks 2–3)

- Langflow chat flow: extract the bug with `gpt-5.4-nano`, ask for missing fields, pick the repo, call `POST /runs`. See [CHAT-AND-LOCAL-MODE.md](CHAT-AND-LOCAL-MODE.md).
- FastAPI with an API key: `POST /runs`, `GET /runs/{id}`, `POST /approvals`, `GET /repos`.
- LangGraph graph with checkpoints in Postgres: classify (nano) → research → reproduce → patch (two attempts) → approval → branch and patch file.
- Research: full LlamaIndex index of the local repo (`code` and `docs`), hybrid search filtered by repository.
- Local git adapter: `git worktree` on `agent/issue-<n>`; your own checkout is never touched.
- Sandbox: Docker with no network and no secrets; runs `pytest` on a copy of the worktree.
- Approval: type `approve 12` in the chat. `interrupt()` pauses the graph until then.
- Langfuse trace for every run.

**Demo:** describe a seeded bug in the chat box. The agent asks one follow-up question, writes a failing test, patches it, waits for `approve`, and leaves `agent/issue-<n>` with a patch file and summary.

### R2: Trust, critic, and summary (week 4)

- Refusals: non-maintainer label, unknown author, instructions inside the issue body. Each is logged, with no work started.
- Append-only audit log.
- Critic node: tests pass, every claim cited, confidence score. Low confidence or an exhausted budget escalates to the maintainer with full context.
- "Not reproduced" path: a comment asking for specific detail, no patch.
- Summary agent: five-part root-cause summary with citations, behind its own approval.

**Demo:** scenes 4, 6, 7 and 8, showing when the agent refuses or chooses not to answer.

### R3: Memory and routing (week 5)

- Repo profiler (Python only in phase 1, with Java and C# detected and reported as "phase 2").
- Incremental refresh on PR merge and on `/agent reindex`; `index_state` and `index_runs` tables.
- `fixes` collection written when an agent PR is merged and its summary approved.
- SQL tool (read-only role) over runs, issues, costs and index tables.
- Router: RAG, SQL, or hybrid, with the route recorded in the trace.

**Demo:** merge the R1 PR and show the `index_runs` row; then ask "where is the date parsing code?" (RAG), "how many fixes merged this week and what did they cost?" (SQL), and "have we fixed a bug like this before?" (hybrid).

### R4: Evaluation and SLOs (week 6)

- 50 golden queries labelled with type, risk, retrieval mode and expected escalation (15 RAG, 10 SQL, 10 hybrid, 10 high-risk, 5 escalation).
- Run the 10 seeded bugs end to end, three times each, for pass^k.
- Red-team set: injection in issue text, forged events, attempts to push outside `agent/*`.
- Small-to-strong model escalation; measure cost and latency both ways.
- SLO report following [VERIFICATION.md](VERIFICATION.md).

**Demo:** the SLO dashboard, the routing confusion matrix, and the cost per issue.

### R5: Demo polish (week 7)

- React (Vite, TypeScript) UI with three screens: runs, approvals, repos and memory.
- Langflow intake flow (Jira or Gmail, decided by open item 22) calling `POST /runs`, and a Langflow Slack flow for approvals.
- Self-hosting guide; demo rehearsal twice in a row; recorded backup of every scene.

**Demo:** the full 5-minute demo.

## Phase 2 (after the capstone)

- Java and C# repositories through the repo profiler: splitter, test command, sandbox image.
- Other code hosts and trackers through the adapters in [INTEGRATIONS.md](INTEGRATIONS.md): GitLab, Bitbucket, CodeCommit, Jira, Zoho.
- Agents split into A2A services.
- Feature requests with spec approval, and the VS Code extension. See [FUTURE-SCOPE.md](FUTURE-SCOPE.md).

## Cut list

Cut from the top. Each release still stands on its own.

1. GitHub draft PRs and Slack approvals (R5): keep the local branch and chat approvals.
2. React UI (R5): demo through the Langflow chat and Langfuse.
3. Graphify code graph: rely on hybrid search alone.
4. Small-to-strong model escalation (R4): run every node on `gpt-5.4` and accept the cost.
5. `conventions` collection (R3): keep only `fixes`.

Do not cut:
- signature checks and the maintainer and author allow-lists
- the approval gates for pushes, PRs, and summaries
- the citation check and the critic
- the RAG, SQL, and hybrid router (20% of the marks)
- the golden set and the security tests

These are what make the system safe to show, and they carry most of the marks.

## Risks

| Risk | Likelihood | Impact | Response |
|---|---|---|---|
| Scope exceeds seven weeks | High | High | Releases are demoable on their own; cut list above; phase 1 is Python and GitHub only |
| Langflow chat flow takes longer than expected | Medium | Medium | Fall back to `POST /runs` from a script or the API docs page for R1; add the chat in R2 |
| Model quality varies between deployments | Medium | Medium | Compare on the seeded set in week 1 and keep the better one |
| Patches pass tests but are wrong | High | High | Human approval; acceptance metric; test coverage stated in each summary |
| Prompt injection in a report | Medium | High | Report text treated as data; tool allow-list; security tests |
| Source code sent to the model provider | Certain with any hosted model | High | Azure OpenAI in the user's tenant; data-handling note in the guide |
| Cost overrun | Medium | Medium | Per-issue budget; two-attempt limit; measured baseline in week 2 |
| Rate limits on the model deployment | Medium | Low | Retry with backoff; surface the limit to the maintainer |

## Definition of done (phase 1)

- The chat-to-branch path works end to end on seeded Python bugs in a local repository, with the API key enforced.
- The router answers RAG, SQL, and hybrid questions, and memory refreshes on merge.
- Every write action needs an approval, and the security tests pass.
- Summaries have citations, and none reaches a reporter without approval.
- The evaluation report exists, with targets met or explained.
- A new user can set up a fork from the guide in under 30 minutes.

## Open questions

1. Which reference repository, and who approves its use.
2. Decided 28 Oct 2026: `gpt-5.4-nano` for cheap steps and `gpt-5.4` for code and summaries. See [AZURE-SETUP.md](AZURE-SETUP.md).
3. The data-handling note for each deployment, including Azure's terms for the chosen resource.

## Reference repository (Phase 0)

Candidates, checked against the GitHub API in October 2026:

| Repo | Licence | Stars | Open issues | Last push | Notes |
|---|---|---|---|---|---|
| [python-attrs/attrs](https://github.com/python-attrs/attrs) | MIT | 5,860 | 174 | 13 Oct 2026 | Largest issue volume for triage; first pick |
| [fastapi/typer](https://github.com/fastapi/typer) | MIT | 20,186 | 48 | 15 Oct 2026 | Smaller backlog; fallback if attrs' suite is slow |
| [pallets/click](https://github.com/pallets/click) | BSD-3-Clause | 17,800 | 86 | 6 Oct 2026 | Larger codebase; less convenient to baseline |

Selection rules:
- Work on a fork. Live runs happen only on the fork, never on the upstream project.
- Upstream issue history is read-only evaluation data, used for the evaluation sets.
- Time the test suite on the build machine. The chosen repo's suite must finish in under ten minutes.
- Choose between the candidates on suite runtime, then on the number of reproducible historical bugs.
