### Create Bug Report Task

## Purpose

- To create a high-quality, actionable bug report in **MCP Jira** that provides the development team with all the necessary information to understand, reproduce, and fix the defect.
- To formalize a finding from a previous investigation or a direct user report into a trackable work item.

Remember as you follow the upcoming instructions:

- The quality of your bug report directly impacts how quickly and effectively the issue can be resolved.
- "Cannot reproduce" is the enemy; your goal is to provide enough detail to make reproduction easy.

## Instructions

### 1. Gather Bug Context

- Ask the user to describe the bug. If this task was not preceded by an "Investigate User Issue" task, you must gather the following essential information:
    - **Summary/Title:** A brief, clear description of the bug.
    - **Description:** What is the problem? What is the impact on the user?
    - **Steps to Reproduce:** A numbered list of the precise steps required to trigger the bug.
    - **Expected Result:** What should have happened if the bug was not present?
    - **Actual Result:** What actually happened?
    - **Environment:** Where was the bug observed (e.g., Production, Staging, specific browser/OS)?

### 2. Enrich with Technical Data (If Necessary)

- Review the information provided by the user. If critical technical evidence is missing, state that you will perform a brief, targeted investigation to find it.
- **Example actions:**
    - "To make this bug report more effective, I will quickly check **MCP Sentry** for related error traces."
    - "I will search the logs in **MCP Grafana** for the relevant session to attach a snippet."
- Add any findings (e.g., Sentry links, log snippets, relevant User IDs) to the bug report context.

### 3. Draft the Jira Ticket

- Inform the user you will now draft the content for the Jira ticket. Structure the content clearly using the following sections:
    - **Title**
    - **Description**
    - **Environment**
    - **Steps to Reproduce**
    - **Expected Result**
    - **Actual Result**
    - **Supporting Evidence** (A section for links, IDs, and log snippets)

### 4. Confirm and Create

- Present the fully drafted ticket content to the user for final approval.
- Once the user confirms the content is correct and complete, state that you are now creating the bug report in **MCP Jira**.

### 5. Provide Ticket ID and Handoff

- After successfully creating the ticket, provide the user with the **Jira Ticket ID and a direct link** to it for future reference.
- Confirm that the bug has been formally logged and is now in the development team's queue.

---
