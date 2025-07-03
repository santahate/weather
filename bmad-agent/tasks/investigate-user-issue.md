# Investigate User Issue Task

## Purpose

- Systematically diagnose a user-reported issue to determine its root cause.
- Provide a clear, accurate, and helpful resolution to the user.
- Create high-quality, actionable bug reports or tasks in Jira when necessary to escalate issues to the development team.

Remember as you follow the upcoming instructions:

- Your role is to be the user's advocate and the development team's first line of defense.
- A thorough investigation saves development time and improves user trust.
- Clear communication is critical at every step.

## Instructions

### 1. Initiate Investigation and Gather Initial Information

A. **Capture the Problem:** Ask the user for a clear and detailed description of the issue. Key information to request includes:
    - A summary of the problem (what happened vs. what was expected).
    - The User ID or email of the affected user.
    - **The precise date and time the issue occurred.**
    - Any error messages they received.
    - Steps they took leading up to the issue.

B. **Check for Known Issues:** Quickly check **MCP Jira** to see if a similar issue has already been reported to avoid duplicate efforts.

### 2. Conduct Systematic Triage (The Investigation Funnel)

Inform the user you will now begin a systematic investigation using all available tools. Follow these steps in order, leveraging findings from one step to inform the next.

A. **Consult Documentation (MCP Confluence):** First, check if the described behavior is actually expected according to the user documentation. This can quickly resolve issues related to user misunderstanding.

B. **Check for Errors (MCP Sentry):** Search **MCP Sentry** for any error traces or exceptions that correlate with the user and the reported timeframe. This is often the fastest way to identify a code-level bug.

C. **Analyze Logs (MCP Grafana & MySQL):**
    <important_note>If the user did not provide a specific time for the event, you must politely ask for it now, as it is crucial for log analysis.</important_note>
    - Use **MCP Grafana** to search and filter logs around the reported time to understand the sequence of events.
    - For more detailed analysis, query the `users_logaction` table directly in **MCP MySQL** to reconstruct the user's exact actions.

D. **Verify Data State (MCP MySQL):** Inspect the application database to check the state of the relevant data. Is the data missing, corrupted, or in an unexpected state that would explain the issue?

E. **Reference the Codebase:** If the cause is still unclear, perform a high-level review of the **current codebase** to understand the intended business logic related to the feature. This is the ultimate source of truth for how the system is designed to work.

### 3. Synthesize Findings and Determine Resolution Path

A. **Summarize Findings:** Present a clear, concise summary of your findings from the investigation to the user.

B. **Determine Root Cause:** Based on your findings, state the most likely root cause.

C. **Propose Next Steps:** Recommend a clear resolution path to the user and ask for their confirmation to proceed. The path will be one of the following:
    - **Path A (Direct Solution):** If the issue was due to user error or a known workaround exists, provide a clear explanation and steps for the user to resolve it.
    - **Path B (Bug Report):** If you have confirmed a bug, inform the user that you will create a bug report in **MCP Jira** for the development team.
    - **Path C (Task/Feature Request):** If the issue is a request for a new feature or a change that is not a bug, inform the user you will create a task ticket in **MCP Jira**.

### 4. Execute and Handoff

- If the user agrees to the creation of a Jira ticket (Path B or C), proceed to create it.
- Ensure the ticket is detailed, including your findings, logs, and steps to reproduce.
- Provide the user with the **Jira Ticket ID and link** for their reference, and confirm that the issue is now being tracked.
