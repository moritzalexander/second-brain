# Source adapters

Adapters translate an authorized source into a small, auditable contract:

- discover eligible item metadata without fetching every large body
- expose a stable source ID
- distinguish ready, unfinished, deleted, and failed items
- render the complete authorized raw source
- never mutate the source system

Connector-backed sources such as Gmail, Slack, Drive, Circleback, or Salesforce usually use the agent platform's connector directly and do not need code in this repository. Local application data benefits from a dedicated read-only adapter.

Every operational adapter should have schema checks, a dry-run or discovery command, and a coverage comparison against stable IDs already stored in the vault.
