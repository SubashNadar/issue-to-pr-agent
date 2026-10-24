# Roadmap

**Audience:** everyone. **Status:** version 1 plan.

## Scope check

The design in [ARCHITECTURE.md](ARCHITECTURE.md) covers three repository providers, two intake channels, a patch loop, memory, a self-hosted deployment, and an extension. That is more than seven weeks of work. The plan below keeps GitHub and one intake channel as the committed core. Everything else is marked as a cut candidate, in the order it would be dropped.

## Phases

### Phase 0: Set up (week 1)
- Choose the reference repository against these criteria: a repository the team controls, a test suite under ten minutes, and clear contribution rules.
- Build the code graph and record its report.
- Agree the memory schema and choose Mem0 or Graphiti.
- Agree the allow-list model and the model-provider policy.

**Exit:** reference repository chosen; graph report generated; decisions 5 and 10 in ARCHITECTURE.md closed.

### Phase 1: GitHub path (weeks 2–3)
- Webhook receiver with signature verification and idempotency.
- Allow-list enforcement for repository issues.
- Research, reproduction, and patch agents over A2A, with the sandbox over gRPC.
- Approval queue for pushes and review requests.

**Exit:** ten seeded issues from allow-listed authors produce draft PRs; non-allow-listed issues produce no work.

### Phase 2: Intake (week 4)
- Gmail or Jira intake flow in Langflow, with custom components.
- Sender verification, the generic reply with rate limit, and duplicate checks.

**Exit:** allow-listed reports create linked issues; other senders get the generic reply at most once a day; forged-sender tests pass.

### Phase 3: Write-back (week 5)
- Summary agent with citation checks.
- Approval before posting to the issue, Jira, or the reporter.
- Memory writes on merge.

**Exit:** summaries posted with approval; uncited claims removed in tests.

### Phase 4: Setup and distribution (week 6)
- Self-hosting guide and Docker Compose stack.
- VS Code extension for provider connection, keys, allow-list, and health checks.
- Test-issue button that runs the full path on a sandbox repository.

**Exit:** a new user completes setup from the guide in under 30 minutes.

### Phase 5: Evaluation and demo (week 7)
- Run the evaluation in [EVALUATION.md](EVALUATION.md).
- Record a three-minute demo.
- Publish the report and the setup guide.

**Exit:** report published, including targets not met.

## Cut list

If the schedule slips, cut in this order:

1. GitLab and Bitbucket adapters (already outside version 1 committed scope)
2. Extension test-issue button (use the guide's manual steps instead)
3. Second intake channel (keep whichever is chosen first)
4. Jira write-back (keep the GitHub comment and email reply)
5. Graphify incremental updates (re-run the full graph after each merge)

Do not cut: allow-list enforcement, signature verification, approval gates, the security test suite, or the citation check. These are what make the system safe to show.

## Risks

| Risk | Likelihood | Impact | Response |
|---|---|---|---|
| Scope exceeds seven weeks | High | High | Cut list above; committed core is GitHub plus one channel |
| Langflow lacks Gmail or Jira components | Confirmed | Medium | Custom components in week 2 as a spike |
| A2A spec changes during build | Medium | Medium | Pin version; isolate in one adapter module |
| Graphify incremental updates unsupported | Medium | Low | Full re-run after merge |
| Memory tool choice is wrong | Medium | Low | Measure retrieval in week 1; swap is contained behind the memory interface |
| Patches pass tests but are wrong | High | High | Human review; acceptance metric; summaries show test coverage of the change |
| Source code sent to an external model | Certain if using a hosted model | High | Decision 10 must be closed before the first run on real code |
| Email deliverability or spam filters | Medium | Low | Use authenticated sending; test with several providers |
| Cost overrun | Medium | Medium | Per-issue budget; measured baseline in week 2 |

## Definition of done (version 1)

- The GitHub path works end to end on seeded bugs, with the allow-list enforced.
- At least one intake channel works end to end with the allow-list and generic reply.
- Every write action requires an approval token, and the security test suite passes.
- The evaluation report exists, with targets met or explained.
- A new user can set up the system from the guide in under 30 minutes.
- The repository's licence, contribution guide, and security policy are in place.

## Open questions

1. Reference repository, and who approves its use.
2. Intake channel for version 1.
3. Model-provider policy for source code.
4. Acceptable cost per issue.
5. Licence and Marketplace publication for the extension.
