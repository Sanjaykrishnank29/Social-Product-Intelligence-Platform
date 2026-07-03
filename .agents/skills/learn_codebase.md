# Skill: Complete Codebase Structural & Execution Decomposition

When the user runs `/learn-codebase`, you must analyze the target codebase or file and generate a breakdown matching this exact technical layout.

---

## 1. Entry Point & Routing Path
Map exactly how execution context flows into this code from the base application layer.
- **Trigger/Route:** What HTTP route, event listener, cron schedule, or function call executes this code?
- **Upstream Dependencies:** What modules or files must execute *before* this file can run safely?
- **Downstream Targets:** Where does data go immediately *after* this file finishes execution?

## 2. In-Depth Component Analysis (File/State/Method)
Break down the code elements inside the file:
- **Core State Variables:** List any local or global state variables tracked within this file, their default initial configurations, and what triggers them to change.
- **Methods & Functions Matrix:**
  | Method Name | Input Parameters | Return Value | Internal Logic & Purpose |
  | :--- | :--- | :--- | :--- |
  | `example: processUser()` | `id: string, roles: string[]` | `Promise<boolean>` | Validates user session token, updates active cache state, and returns true if authorized. |

- **Algorithmic Complexity Bounds:** Document the exact computational cost of any complex array loops, search behaviors, or transformation tasks:
  $$\text{Time Complexity} = O(N)$$
  $$\text{Space Complexity} = O(N)$$

## 3. Runtime Environment & Commands
Provide the exact CLI commands required to operate this specific slice of the codebase.
- **Prerequisites:** What background services (e.g., Docker containers, Local Redis, Postgres DB instances) must be running?
- **Execution Commands:** Give the direct terminal strings to launch, spin up, or hot-reload this specific code module.
- **Environment Flags:** Detail any mandatory `.env` or system properties required by this file to run without crashing.

## 4. Operational Testing & Verification Protocol
Explain exactly how to test this code to confirm whether it is working properly or broken after edits.
- **Automated Tests:** Provide the precise test runner terminal command (e.g., `npm run test -- filepath.test.ts` or `pytest path/to/test.py`) designed to validate this module.
- **Manual Verification Steps:** Provide a step-by-step manual triage pipeline (e.g., an exact `curl` request, a specific Postman payload, or log monitoring targets) to confirm operational integrity.
- **Expected Success Indicators:** What specific string, response object, or standard out (`stdout`) message proves this code is working perfectly?
- **Failure Indicators:** What typical error codes, stack traces, or logs will surface immediately if the logic breaks during modification?
