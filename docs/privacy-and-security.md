# Privacy and security

Second Brain handles source material that may contain personal, customer, company-confidential, or regulated information. The architecture is private by default.

## Separate template from data

Use two locations:

- a public or shareable repository containing structure, skills, tests, and placeholders
- a private operational vault containing knowledge, source evidence, indexes, and automation state

Do not make the private vault a clone of this public repository.

## Source authorization

Enable only sources the user is authorized to process. Prefer read-only adapters. A local database integration must never modify the source application database.

Treat authentication and filesystem permission errors as blockers. Do not record “no new items” and do not advance a cursor when the source could not be read.

## Raw evidence

Raw transcripts and threads are useful for verification but carry the highest privacy risk. Keep them in the private vault, inherit source access controls, and define a retention policy appropriate to the organization.

Generated summaries do not automatically become safe to share. They may reproduce sensitive facts.

## Shared or multiplayer graphs

Do not connect a shared graph directly to each member's personal email, private chat, or local meeting store. Use a publishing boundary:

```text
private personal graph -> candidate share queue -> policy/redaction -> shared team graph
```

Every published record should include:

- source and timestamp
- publisher or responsible owner
- audience or confidentiality class
- provenance link available to authorized users
- confidence and last-verified timestamp where relevant
- supersession links when a newer fact replaces it

Recommended audience classes are `private`, `deal-team`, `function-team`, `leadership`, and `company`.

## Write-back

Reading a CRM or document system is different from writing to it. Keep proposed CRM updates, emails, messages, and document edits in draft form until a user explicitly approves the external action.

## Public repository checks

The included validator detects common leaks such as local home paths, email addresses, database files, operational Markdown under ignored knowledge directories, and unexpanded user-specific placeholders. It is a backstop, not a substitute for review.
