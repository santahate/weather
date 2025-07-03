# Generate MR Description Task

## Purpose

- Turn a completed merge request (plus optional Jira ticket) into a structured, Confluence-ready documentation page following `mr-description-tmpl`.
- Ensure documentation accurately reflects delivered functionality, technical changes, and aligns with acceptance criteria.

## Instructions

### 1. Request and Confirm Identifiers

- Ask the user to provide:
  1. **Merge Request ID** (required)
  2. **Jira Ticket ID** (optional)
- Confirm with the user that these are correct before proceeding.

### 2. Gather Context

1. **Analyse the Merge Request:**
   - Fetch MR title, description, commits, and full diff.
   - Identify affected modules, files, database migrations, settings, and UI components.
2. **Review Jira Ticket (if provided):**
   - Read description, comments, acceptance criteria.
3. **Consult Codebase (High-Level):**
   - Skim changed files to understand implementation choices and hidden impacts.

### 3. Draft Documentation Using Template

- Populate each section of `mr-description-tmpl`:
  - **Purpose**: Synthesize business value or problem solved.
  - **URL / Entry Points**: List new or altered routes/endpoints/screens.
  - **Functionality**: Bullet major functional points (positive & edge cases where relevant).
  - **Interface Description**: Detail UI/UX changes; include `![Screenshot](<add_here>)` placeholders.
  - **Configuration / Settings**: Note env vars, feature flags, permissions.
  - **Database / API Changes**: Summarise migrations and API deltas.
  - **Risks & Rollback**: Flag risks and quick disable steps.
  - **Related Links**: Insert MR & Jira URLs.

### 4. Review & Iterate

- Present the draft to the user for review.
- Capture feedback on missing details, incorrect info, or formatting.
- Iterate until the user approves.

### 5. Finalise Documentation

- Provide the final Markdown document ready for Confluence copy-paste.
- Indicate screenshot placeholders clearly.

---

<important_note>Always keep the output in English unless the user explicitly requests Ukrainian. Place emojis sparingly per Emoji Communication Guidelines.</important_note>
