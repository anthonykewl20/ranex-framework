# 📐 Technical Design: TEST_FEATURE
Status: Draft (AI must not code yet)

## 1. Architecture Layers
- **Routes:** (Define endpoints, e.g., POST /api/{feature}/...)
- **Service:** (Define public methods and return types)
- **Models:** (Define DB Schema and relationships)

## 2. State Machine (The Contract)
- **Initial State:** ...
- **States:** [State A, State B, ...]
- **Transitions:**
    - A -> B (Trigger?)
    - B -> C (Trigger?)

## 3. Coding Standards Compliance (Mandatory)
The AI must explicitly agree to these standards:
- [ ] **Naming:** Snake_case for functions, PascalCase for classes.
- [ ] **Error Handling:** Use `try/except` blocks. Raise explicit `HTTPException`.
- [ ] **DRY:** Move shared logic to `app/commons/`.
- [ ] **Docstrings:** All public functions must have docstrings.

## 4. Configuration & Environment (Centralized Config)
**STOP:** Do not use hardcoded strings or numbers.
List all configuration variables required for this feature:
| Variable Name | Default Value | Description |
|--------------|---------------|-------------|
| e.g., `MAX_RETRIES` | `3` | Number of payment attempts |
| e.g., `STRIPE_KEY` | `(Secret)` | API Key for provider |

These must be added to app/config.py.

## 5. Verification Plan (The Holodeck)
Define the Simulation Scenario that proves this works.
**Format:** `tests/simulations/test_feature_flow.yaml`

- [ ] Simulation: `tests/simulations/test_feature_flow.yaml`