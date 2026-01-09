# Prompt Library (Spec-driven + TDD + Compounding)

Use these prompts with your organization-approved AI assistant.

## 1) Clarify before drafting
> You are my engineering partner. Before you write anything, ask up to 10 clarifying questions that would materially change the spec (requirements, metrics, schema, rollout). Then draft the spec using our template. Highlight assumptions and open questions.

## 2) Acceptance criteria (testable)
> Convert the spec into 8–12 acceptance criteria written as testable statements. Label them AC-1, AC-2, etc. Include edge cases and failure behavior.

## 3) Tests only (no implementation)
> Using the acceptance criteria below, write pytest tests only. Each test must reference the AC label in a comment. Do not write implementation.

## 4) Minimal implementation
> Implement only what’s needed to pass the failing tests. Keep changes small. Do not change tests unless they conflict with the spec—if so, explain and propose a spec update.

## 5) PR comments → rules
> Here are recurring PR review comments. Convert them into: (a) PR checklist items, (b) agent instructions, and (c) one automated gate we can add in CI. Keep everything short and enforceable.

## 6) PR summary
> Summarize this PR in 8 bullets: what changed, why, how verified, risks, rollout plan. Mention which acceptance criteria are satisfied.
