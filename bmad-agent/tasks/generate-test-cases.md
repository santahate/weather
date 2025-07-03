# Generate Test Cases Task

## Purpose

- Transform user stories, requirements, and technical context into a comprehensive, structured set of test cases.
- Define test scenarios that cover positive paths, negative paths, and critical edge cases to ensure product quality.
- Provide a clear, actionable testing plan for execution by a manual tester or for future automation efforts.

Remember as you follow the upcoming instructions:

- The quality of your test cases directly impacts the final product quality.
- Your output must be clear enough for any team member to understand and execute the tests.
- Your goal is to find defects before the user does, by thinking critically about how the system can fail.

## Instructions

### 1. Request and Confirm the Target for Testing

- Before generating test cases, ask the user to provide the primary identifier for the feature to be tested (e.g., a **Jira Ticket ID**).
- Confirm with the user that this is the correct feature to focus on for the current testing cycle.

### 2. Gather and Synthesize All Available Context

Inform the user that you will now perform a comprehensive review of all related materials to build a deep understanding of the feature.

A. **Analyze the Jira Ticket:** Thoroughly review the specified Jira ticket, paying close attention to the description, comments, and especially the **Acceptance Criteria (ACs)**. This is your primary source for testable requirements.

B. **Review Attached Documentation:** Examine all linked documents for broader context. This includes the **Product Requirements Document (PRD)** for business goals, **Architecture documents** for technical implementation context, and **UI/UX specifications** for user flow and design expectations.

C. **Consult the Codebase (High-Level):** Perform a high-level review of the relevant parts of the **current codebase**. Your goal is not to debug the code, but to understand implementation patterns, identify areas of high complexity or risk, and see how new code integrates with existing modules. This will inform where to focus your testing efforts.

C2. **Assess Code Changes (Impact Analysis):** When reviewing code diffs, identify every system component and functionality affected. Ensure that test cases are created for these impacted areas, even if they are not explicitly referenced in the Jira ticket or acceptance criteria.

D. **Confirm Understanding:** After your review, present a concise summary of your understanding of the feature's functionality and the scope of testing to the user. Ask for confirmation before proceeding.
    - *Example: "Based on my review, the goal is to test the new checkout flow, ensuring it supports both credit card and PayPal payments, and correctly calculates shipping costs based on user location. Is this understanding correct?"*

### 3. Design and Generate Test Cases

A. **Define Test Scenarios:** Inform the user you will first outline the high-level test scenarios to ensure full coverage. Group them into logical categories:
    - **Positive Scenarios (Happy Path):** The system works as expected with valid inputs.
    - **Negative Scenarios:** The system gracefully handles invalid inputs, errors, and unexpected user actions.
    - **Boundary and Edge Cases:** The system behaves correctly at the limits of its input ranges (e.g., minimum/maximum values, empty fields).
    - **UI/Usability Scenarios:** The user interface is consistent, intuitive, and matches the design specifications.

B. **Draft Detailed Test Cases:** For each scenario, create detailed, structured test cases. Each test case must include:
    - **Test Case ID:** A unique identifier.
    - **Title:** A brief, descriptive summary.
    - **Preconditions:** What must be true before the test can start.
    - **Steps to Reproduce:** A clear, numbered list of actions to perform.
    - **Expected Result:** A precise description of the expected outcome.

### 4. Review and Finalize

A. **Present Draft for Review:** Present the complete set of drafted test cases to the user for review.
B. **Incorporate Feedback:** Ask the user for feedback, specifically if any scenarios are missing or if any steps or expected results are unclear. Update the test cases based on their input.
C. **Produce Final Document:** Once approved, generate the final, clean test case document in the Markdown format

## Test Case Output Format (STRICT)

When presenting each test case you **must** reproduce the following plain-text structure **exactly in the order shown below**.
Do **not** add Markdown headings (e.g. `#`, `##`) or any additional decoration—the downstream import tool expects a raw text block where each item appears on its own line.
Replace the angle-bracket placeholders with the concrete values for your test case.

```
<Title of the Test Case>
Active
<Area / Module>          # e.g. Client interactions
Template
Case (steps)
Tags
<Comma-separated tags, e.g. clients>
Description
<Short functional description of the test case>

<ID>
Steps
1
<Step description #1>
<Step description #2>
...
Expected
<Expected result for steps 1-N>

2
<Scenario title or Step Group #2>
<Step description #1>
...
Expected
<Expected result for the second scenario>

# ➡️  Continue enumerating additional scenarios/step-groups following the same pattern.
```

Key rules to remember:
1. Maintain the **exact sequence** and **line breaks** shown above; automated parsers rely on them.
2. Keep **steps** concise but explicit—each user action or system trigger belongs on its own line.
3. The **Expected** block must fully describe the system behaviour that confirms success.
4. Leave a single blank line between the `Description` block and the numeric `<ID>` that starts the Steps section.
5. Use the **same language** (Ukrainian or English) as the requirements provided by the user.

---
