import re
from textwrap import dedent


def get_requirements_template(feature: str) -> str:
    return dedent(
        f"""
        # 📝 Requirements Specification: {feature.upper()}
        Status: Draft (AI must not code yet)

        ## 1. Business Objective
        (What problem are we solving? Why does this feature exist?)

        ## 2. User Stories
        - As a [Role], I want to [Action], so that [Benefit].
        - ...

        ## 3. Business Rules (The Logic Firewall)
        - [Rule 1] e.g., Cannot refund if status is 'Idle'
        - [Rule 2] e.g., Maximum transaction limit is $5000
        - [Rule 3] ...

        ## 4. Security Constraints
        - [ ] Authentication Required?
        - [ ] Input Sanitization Needs?
        - [ ] Data Privacy (PII)?
        """
    ).strip()


def get_system_context() -> str:
    return dedent(
        """
        # RANEX FRAMEWORK: SYSTEM CONTEXT (v0.0.1)
        You are a Senior Ranex Architect. You DO NOT write generic Python code. You write Ranex-Compliant Hybrid Code.

        ## 1. THE LAWS OF PHYSICS (Strict Enforcement)
        - **NO** `utils/`, `helpers/`, `lib/` or `common/` folders. These are BANNED.
        - **ALL** shared logic goes in `app/commons/` (Pure functions only).
        - **ALL** business logic goes in `app/features/{name}/` (Vertical Slices).
        - **Feature Structure:** Each feature MUST have exactly 4 files: `routes.py`, `service.py`, `models.py`, `state.yaml`.
        - **Layering:** Routes → Service → Models. Never skip a layer.

        ## 2. THE BINARY FILE STRUCTURE (Do not hallucinate)
        /ranex-project-root
        ├── .ranex/
        │   ├── atlas.db                # [LAYER 2] Vector DB of ALL functions
        │   ├── config.toml             # Project constraints
        │   └── audit/                  # Cryptographic audit logs
        ├── Cargo.toml                  # Rust dependencies
        ├── pyproject.toml              # Python dependencies
        ├── maturin.toml                # Build configuration
        ├── src/                        # [KERNEL SPACE] - The Rust Core
        │   ├── lib.rs                  # Logic Firewall & State Engine
        │   ├── guardrails.rs           # [LAYER 2] Structure Police
        │   ├── state_machine.rs        # State validation engine
        │   ├── validator.rs            # Import & code validator
        │   ├── atlas.rs                # Semantic deduplication
        │   └── bin/
        │       └── ranex_mcp.rs        # [LAYER 1] MCP Server binary
        └── app/                        # [USER SPACE] - Python Application
            ├── main.py                 # Application entry point
            ├── commons/                # [STRICT] Shared Pure Logic
            │   ├── validators.py
            │   ├── formatters.py
            │   ├── math_utils.py
            │   └── date_utils.py
            └── features/               # [STRICT] Vertical Slices
                └── {feature_name}/
                    ├── routes.py       # FastAPI endpoints
                    ├── service.py      # Business logic (@Contract)
                    ├── models.py       # Pydantic schemas
                    └── state.yaml      # State machine definition

        ## 3. CODING STANDARDS
        - **Config:** NEVER hardcode. Use `app.config` or pass params.
        - **State:** NEVER set status manually. Use `ctx.transition("StateName")`.
        - **Imports:** NEVER import `models` inside `routes`. (Layer Violation).
        - **Error Handling:** Raise `HTTPException` in routes, custom errors in service.

        ## 4. ONE-SHOT EXAMPLE (Mimic this style exactly)

        ### `app/features/subscription/service.py`
        ```python
        from ranex import Contract, StateMachine
        from .models import SubRequest, SubResponse

        @Contract(feature="subscription", input_model=SubRequest, output_model=SubResponse)
        def create_subscription(req: SubRequest):
            ctx = StateMachine.get_current()
            # 1. Transition State
            ctx.transition("Active")

            # 2. Business Logic
            if req.plan == "enterprise":
                notify_sales(req.user_id)

            return SubResponse(status="active")
        ```

        ### `app/features/subscription/state.yaml`
        ```yaml
        initial: Inactive
        states: [Inactive, Active, Cancelled]
        transitions:
          Inactive: [Active]
          Active: [Cancelled]
        ```
        """
    ).strip()


def get_feature_override_template(feature: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", feature.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_") or feature.strip().lower()
    title = slug.replace("_", " ").title()

    return dedent(
        f"""
        ## FEATURE OVERRIDE: {title}
        Target Directory: `app/features/{slug}/`

        ### 1. Feature Files (Immutable Contract)
        - `app/features/{slug}/routes.py`  — FastAPI endpoints. Only call service layer.
        - `app/features/{slug}/service.py` — Business logic guarded by `@Contract`.
        - `app/features/{slug}/models.py`  — Pydantic schemas & ORM models.
        - `app/features/{slug}/state.yaml` — State machine defining valid transitions.

        ### 2. Required Specs
        - Requirements: `docs/specs/001_{slug}_reqs.md`
        - Design: `docs/specs/002_{slug}_design.md`

        ### 3. Guardrails For {title}
        - Routes NEVER import models directly. Use service layer only.
        - Service MUST call `ctx.transition(...)` for every state change.
        - Shared helpers MUST live in `app/commons/`.
        - Database schema changes MUST be mirrored in `models.py` and migrations.

        ### 4. AI Prompt Addendum
        When generating code for `{slug}`, prepend this block to the system context so the AI knows which slice it owns.
        "Use the `{slug}` feature folder. If logic feels reusable, move it to `app/commons/` and import it."
        """
    ).strip()


def get_design_template(feature: str) -> str:
    return dedent(
        f"""
        # 📐 Technical Design: {feature.upper()}
        Status: Draft (AI must not code yet)

        ## 1. Architecture Layers
        - **Routes:** (Define endpoints, e.g., POST /api/{{feature}}/...)
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
        **Format:** `tests/simulations/{feature}_flow.yaml`

        - [ ] Simulation: `tests/simulations/{feature}_flow.yaml`
        """
    ).strip()
