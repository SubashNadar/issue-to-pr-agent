# Roadmap

**Audience:** everyone. **Status:** version 1 plan.

## Scope check

**Decided for phase 1:** intake is Gmail only, and the repository provider is GitHub only. Jira and Zoho are future intake channels. GitLab, Bitbucket, AWS CodeCommit, and Azure DevOps are future providers. Each user supplies their own API keys, so cost is not a constraint in this phase. Forks are allowed.

The design in [ARCHITECTURE.md](ARCHITECTURE.md) covers the full target. That is more than seven weeks of work, so the plan below keeps GitHub and Gmail as the committed core. Everything else is a cut candidate, in the order it would be dropped.

## Phases

### Phase 0: Set up (week 1) — partly done
- Choose the reference repository against these criteria: a repository the team controls, a test suite under ten minutes, and clear contribution rules.
- Build the code graph and record its report.
- Agree the memory schema and choose Mem0 or Graphiti.
- Agree the allow-list model and the model-provider policy. The allow-list model is decided and implemented. The model-provider policy is decided: users bring their own keys.

**Exit:** reference repository chosen; graph report generated; memory decision closed.

### Phase 1: Trust layer and GitHub webhook — done
- Webhook receiver with signature verification and idempotency.
- Allow-list enforcement for repository issues, with the labeller checked against the maintainer list.
- Email sender verification (SPF and DKIM, aligned to the sender's domain), automated-sender detection, and the generic reply limited to one per sender per day.
- Append-only audit log of every decision.

**Exit:** 43 tests pass. Signed, allow-listed, labelled events queue a job; everything else is ignored, denied, or dropped, and every outcome is audited.

### Phase 2: Gmail intake and the fix loop (weeks 2–4)
- Gmail connector: read labelled messages through the Gmail API, and send replies. Uses the user's own OAuth credentials.
- Intake flow: extract fields, validate, check for duplicates, create the GitHub issue, link it to the source message.
- Research, reproduction, and patch agents over A2A, with the sandbox over gRPC.
- Approval queue for pushes and review requests.

**Exit:** ten seeded issues from allow-listed senders and authors produce draft PRs; everyone else produces no work.

### Phase 3: Write-back (week 5)
Phase numbers are kept for continuity with the earlier plan. Phase 1 is complete; phases 2 to 5 are next.
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

1. Future providers: GitLab, Bitbucket, AWS CodeCommit, Azure DevOps (already outside the committed scope)
2. Future intake: Jira and Zoho (already outside the committed scope)
3. Extension test-issue button (use the guide's manual steps instead)
4. Jira and Zoho write-back (not in scope; GitHub comment and Gmail reply remain)
5. Graphify incremental updates (re-run the full graph after each merge)

Do not cut: allow-list enforcement, signature verification, approval gates, the security test suite, or the citation check. These are what make the system safe to show.

## Risks

| Risk | Likelihood | Impact | Response |
|---|---|---|---|
| Scope exceeds seven weeks | High | High | Cut list above; committed core is GitHub plus Gmail |
| Langflow lacks a Gmail component | Confirmed | Medium | Gmail connector as a Python module called from the intake flow |
| Gmail forwarding breaks SPF | Medium | Low | Such mail is dropped, not trusted; documented behaviour |
| Users' Gmail OAuth setup is hard | Medium | Medium | Guided setup in the extension; clear steps in the guide |
| A2A spec changes during build | Medium | Medium | Pin version; isolate in one adapter module |
| Graphify incremental updates unsupported | Medium | Low | Full re-run after merge |
| Memory tool choice is wrong | Medium | Low | Measure retrieval in week 1; swap is contained behind the memory interface |
| Patches pass tests but are wrong | High | High | Human review; acceptance metric; summaries show test coverage of the change |
| Source code sent to an external model | Certain if using a hosted model | High | Decision 10 must be closed before the first run on real code |
| Email deliverability or spam filters | Medium | Low | Use authenticated sending; test with several providers |
| Cost overrun | Medium | Medium | Per-issue budget; measured baseline in week 2 |

## Definition of done (version 1)

- The GitHub path works end to end on seeded bugs, with the allow-list enforced.
- Gmail intake works end to end with sender verification, the allow-list, and the generic reply.
- Forks of the repository can be configured with their own keys and allow-list.
- Every write action requires an approval token, and the security test suite passes.
- The evaluation report exists, with targets met or explained.
- A new user can set up the system from the guide in under 30 minutes.
- The repository's licence, contribution guide, and security policy are in place.

## Open questions

1. Reference repository, and who approves its use.
2. Whether source code may be sent to a hosted model provider. Users bring their own keys; the default deployment still needs a documented data-handling note.
3. Licence and Marketplace publication for the extension.
