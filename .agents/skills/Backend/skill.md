# FastAPI Production-Grade Backend Engineering Skill

## Purpose

Standards for building a robust, resilient, secure, maintainable, observable, and testable **FastAPI modular monolith**.

Core principles:
- Correctness before cleverness
- Explicit business rules
- Strong module boundaries
- Transactional consistency
- Secure-by-default APIs
- Idempotent retry-safe operations
- Failure-aware integrations
- Automated testing
- Safe database migrations
- Observable production behavior

This is a **modular monolith**, not a microservice system. Keep deployment and operational complexity low while maintaining strong internal boundaries.

## Architecture

Recommended request flow:

    Router / API
        ↓
    Service / Application Layer
        ↓
    Repository / Data Access
        ↓
    SQLAlchemy / PostgreSQL

Cross-cutting concerns:
- Authentication
- Authorization
- Configuration
- Logging
- Error handling
- Observability
- Storage
- External integrations

Rules:
- Routers translate HTTP concerns; they do not contain business logic.
- Services enforce business rules and orchestrate transactions.
- Repositories handle persistence/query concerns.
- Do not return HTTP responses from repositories/services.
- Avoid random cross-module imports that bypass module boundaries.

## Database Engineering

Use:
- PostgreSQL
- SQLAlchemy 2.x
- AsyncSession for asynchronous database I/O
- Alembic for migrations

Never use `Base.metadata.create_all()` as production schema management. Use reviewed Alembic migrations.

### Transactions

Put transaction boundaries at the service/application boundary.

A multi-step business operation should normally execute in one transaction:

    service
      └── transaction
            ├── repository operation
            ├── repository operation
            └── repository operation
                 ↓
               commit

Avoid committing inside every repository method.

### Sessions

- Normally use one request-scoped AsyncSession.
- Never share sessions across concurrent requests.
- Do not store sessions globally.
- Roll back on failure.
- Close sessions reliably.
- Avoid long-running external operations while holding DB transactions unless necessary.

### Connection Pool

Configure and monitor pool size, max overflow, timeout, and connection health. Size the pool against PostgreSQL limits and deployment replica count; do not blindly increase it.

## ORM Models

Use SQLAlchemy 2.x typed mappings with explicit `Mapped[...]` fields.

Define explicitly:
- Primary keys
- Foreign keys
- Nullability
- Unique constraints
- Useful indexes
- Relationships

Enforce invariants in the database where possible. Examples:
- Unique email
- Unique Google subject
- Unique `(test_id, question_id)`
- Unique `(test_id, question_number)`
- Unique `(test_id, student_id, attempt_number)`

Avoid N+1 queries. Use loading strategies intentionally (`selectinload`, `joinedload`, or explicit queries).

## Pydantic Schemas

Keep API schemas separate from SQLAlchemy models.

Use separate request/response schemas when their contracts differ. Never expose ORM objects blindly.

Pydantic handles:
- Type validation
- Format validation
- Request constraints
- Serialization

The service layer handles:
- Business rules
- Authorization decisions
- State transitions
- Cross-entity validation

## Business Logic

Business rules belong in services/application logic, not routers, repositories, or arbitrary ORM hooks.

Do not trust client-provided:
- User IDs
- Roles
- Ownership
- Status values
- Security-sensitive timestamps

Derive security-sensitive values from authenticated server-side context.

## State Machines

Explicitly define valid state transitions.

Example:

    Test:
        DRAFT → PUBLISHED → CLOSED

    Attempt:
        IN_PROGRESS → SUBMITTED → COMPLETED
        IN_PROGRESS → EXPIRED

    Evaluation:
        PENDING → IN_PROGRESS → COMPLETED

Create explicit service operations such as:
- `publish_test()`
- `submit_attempt()`
- `replace_submission()`
- `start_evaluation()`
- `complete_evaluation()`

Reject invalid transitions deterministically.

## API Design

Version APIs:

    /api/v1/...

Role-oriented namespaces are appropriate:

    /api/v1/student/...
    /api/v1/teacher/...
    /api/v1/admin/...

Design APIs around business capabilities rather than simply exposing tables.

Prefer explicit actions for meaningful state transitions, e.g.:

    POST /tests/{test_id}/publish

Use correct HTTP semantics and consistent status codes.

## Idempotency

Operations that can be retried and could otherwise duplicate business effects must be idempotent.

Important cases:
- File submissions
- Webhooks/callbacks
- Payment-like operations
- Retryable creation operations

Use an `Idempotency-Key` where appropriate. Persist idempotency state in PostgreSQL/Redis as required; do not use process-local dictionaries in production.

Technical retries must not accidentally consume business quotas.

## Concurrency

Assume concurrent requests can occur.

For business-critical counters and state transitions use:
- Transactions
- Row-level locks (`SELECT ... FOR UPDATE`) where appropriate
- Unique constraints
- Atomic SQL updates
- Correct transaction isolation

Do not use Python locks as a substitute for database concurrency control in a multi-worker deployment.

## Authentication and Authorization

Authentication answers **who are you?** Authorization answers **what may you do?**

For Google authentication:
- Verify the ID token on the backend.
- Use Google's stable `sub` as the identity key.
- Verify issuer, audience, expiry, and required claims.
- Obtain application role/status from PostgreSQL.

For admin password authentication:
- Use Argon2id/password hashing.
- Never store plaintext passwords.
- Never log credentials.

Authorization must be enforced server-side for every protected operation.

## Security

Secure by default.

Never:
- Trust client-provided ownership/user identity
- Return raw internal exceptions
- Log passwords or access/refresh tokens
- Build SQL through string concatenation
- Disable TLS verification in production
- Expose unrestricted object-storage buckets

Validate uploaded files for authorization, size, type, and content as required.

Use generated storage keys instead of user-controlled filesystem/object paths.

## File Storage

Store large PDFs in MinIO/S3 and metadata in PostgreSQL.

    PostgreSQL:
        storage_key
        file_name
        file_type
        file_size
        timestamps

    MinIO/S3:
        actual PDF

PostgreSQL and object storage do not share one transaction. Design for partial failures.

Recommended upload sequence:

    1. Validate request
    2. Authorize
    3. Upload object
    4. Commit DB metadata
    5. Reconcile/clean orphan objects if DB commit fails

Never delete the only valid object before the replacement DB state is safely committed.

## Error Handling

Define domain/application exceptions such as:

    ResourceNotFoundError
    PermissionDeniedError
    InvalidStateTransitionError
    ConflictError
    ValidationError

Map them to HTTP responses at the API boundary.

Unexpected exceptions should be logged with correlation context and returned as safe generic errors. Never expose stack traces in production.

## Logging

Use structured logging and request/correlation IDs.

Useful fields:
- timestamp
- level
- service
- environment
- request_id
- user_id where appropriate
- route
- method
- status_code
- duration_ms
- exception type

Never log passwords, tokens, secrets, or sensitive documents.

## Observability

Production observability should include:

### Logs
Structured application logs.

### Metrics
Track:
- Request count
- Latency
- HTTP error rate
- Database errors
- Pool usage
- Upload failures
- Authentication failures
- Background job failures

### Tracing
Use OpenTelemetry when useful, including tracing through HTTP → service → PostgreSQL → object storage.

Health endpoints:

    /health/live
    /health/ready

Liveness should indicate process health. Readiness should indicate whether the application can serve traffic. Do not make liveness depend on every external dependency.

## Configuration

Use Pydantic Settings and environment variables.

Never hard-code secrets or credentials.

Typical settings:

    APP_ENV
    DATABASE_URL
    DATABASE_POOL_SIZE
    GOOGLE_CLIENT_ID
    STORAGE_ENDPOINT
    STORAGE_BUCKET
    STORAGE_ACCESS_KEY
    STORAGE_SECRET_KEY
    LOG_LEVEL

Separate development, test, staging, and production configuration.

Fail fast when mandatory production configuration is missing.

## Dependency Injection

Use FastAPI dependency injection for:
- Database sessions
- Authenticated user context
- Authorization dependencies
- Configuration
- Request-scoped dependencies where useful

Do not hide major business operations inside dependencies.

## Async Programming

Use async for I/O-bound work when the underlying library supports it.

Do not perform blocking calls inside async endpoints. CPU-heavy operations such as large PDF processing should use worker processes/background infrastructure when needed.

## External Integrations

Treat external systems as unreliable.

Implement as appropriate:
- Timeouts
- Bounded retries
- Exponential backoff
- Idempotency
- Failure classification
- Structured logging

Only retry operations that are safe to retry or protected by idempotency.

## Query Performance

Avoid unbounded queries and unnecessary `SELECT *`.

Use indexes based on real query patterns. Do not index every column.

Always consider:
- Query plans
- Joins
- Indexes
- Pagination
- N+1 behavior

## Pagination

Never return unbounded collections.

Use page-size limits and stable ordering. Prefer cursor/keyset pagination for large datasets; offset pagination is acceptable for smaller administrative datasets.

## Validation

Validate at three layers:

    API boundary       → Pydantic
    Business rules     → Service
    Data integrity     → PostgreSQL

Do not depend on frontend validation for correctness or security.

## Testing Strategy

Use multiple testing levels.

### Unit Tests
Test pure business logic:
- Deadline calculations
- State transitions
- Replacement rules
- Authorization decisions

### Integration Tests
Use a real PostgreSQL test database where practical. Test:
- Constraints
- Relationships
- Queries
- Transactions
- Migrations

### API Tests
Test:
- Authentication
- Authorization
- Validation
- Status codes
- Response schemas
- Error handling

### End-to-End Tests
Test critical journeys such as:

    Teacher creates test
       ↓
    Publishes test
       ↓
    Student accesses paper
       ↓
    Student submits answer
       ↓
    Teacher evaluates
       ↓
    Student views evaluation

Also test concurrency and failure scenarios where business correctness depends on them.

## Migration Discipline

Schema change workflow:

    Modify ORM model
        ↓
    Generate/review Alembic migration
        ↓
    Test migration
        ↓
    Run in staging
        ↓
    Deploy

Always review autogenerated migrations manually.

For risky production changes prefer:

    Expand → Migrate → Contract

Avoid destructive changes without a rollback/data migration plan.

## Caching

Do not add Redis merely because it is common.

Cache only measured bottlenecks or clearly expensive/stable reads.

Every cache should have:
- Defined key
- TTL
- Invalidation strategy
- Acceptable staleness model

Critical business state must remain in the database/source of truth.

## Background Work

FastAPI `BackgroundTasks` is suitable only for lightweight, non-critical work where process failure can safely lose the task.

Use durable workers/queues for important jobs such as:
- Large PDF processing
- Email delivery
- Notifications
- Long-running cleanup

Durable jobs should be idempotent, retryable, and observable.

## Scheduled Jobs

Do not rely on an in-process scheduler when multiple replicas may execute the same job.

Use an external scheduler or durable job system. Scheduled jobs must be idempotent and observable.

## API Documentation

Every production endpoint should have:
- Clear summary
- Request schema
- Response schema
- Authentication requirements
- Expected error responses
- Useful descriptions

OpenAPI should remain a stable public contract.

## Code Quality

Recommended tools:
- Ruff
- pytest
- mypy or pyright where appropriate
- pre-commit

CI pipeline:

    Format
      ↓
    Lint
      ↓
    Type check
      ↓
    Unit tests
      ↓
    Integration tests
      ↓
    Migration validation
      ↓
    Build
      ↓
    Deploy

Do not merge code with failing quality gates.

## Dependency Management

Keep dependencies minimal and maintained.

Before adding a dependency ask:
1. Is it genuinely needed?
2. Is it maintained?
3. Does it fit the architecture?
4. Does it introduce security risk?
5. Can an existing dependency solve the problem?

Regularly scan dependencies for vulnerabilities.

## Docker and Deployment

Production containers should:
- Use multi-stage builds where beneficial
- Run as non-root
- Install deterministic dependencies
- Contain only required runtime dependencies
- Use environment configuration
- Provide health checks where appropriate

## Graceful Shutdown

Handle SIGTERM and cleanly close:
- Database connections
- External clients
- Workers/background resources

## Resilience Review

For every important operation explicitly answer:

1. What if PostgreSQL fails?
2. What if object storage fails?
3. What if the client retries?
4. What if two requests arrive concurrently?
5. What if the process crashes halfway through?
6. What if an external service times out?
7. What if the request succeeds but the response is lost?
8. What if an operation is duplicated?

## Auditability

For important administrative/teacher operations consider audit records for:
- Test publication/closure
- Question archival/modification
- Evaluation completion
- Submission replacement
- Permission changes

Record:
- Actor
- Action
- Entity
- Entity ID
- Timestamp
- Relevant metadata

Centralize audit behavior where practical rather than duplicating it across routers.

## CA Test Series Domain Rules

Current domain rules include:

### Test collaboration

If multiple teachers can work on one test, use a junction table:

    test_teachers(test_id, teacher_id, ...)

Do not encode many-to-many relationships as JSON arrays or comma-separated IDs.

### Attempts

A `test_attempt` represents one student's assessment cycle. It is not a PDF version.

### Submission correction window

The first confirmed submission starts the correction window. Replacement uploads during the window do not create new attempts.

### Re-attempt

A deliberate re-attempt after evaluation creates a new `test_attempt`.

### Question paper immutability

Once a test is published, its generated question paper should be immutable. Later question-bank changes must not silently modify an already-issued paper.

Business rules belong in services and must have dedicated tests.

## Avoid Premature Microservices

Keep the system as a modular monolith unless there is a concrete operational, scaling, deployment, or organizational reason to split it.

First establish:
- Strong module boundaries
- Stable APIs
- Reliable transactions
- Observability
- Tests
- Clear ownership

A modular monolith can later be decomposed if needed.

## Production Readiness Checklist

### Code
- [ ] Clear module boundary
- [ ] Type hints
- [ ] No business logic in routers
- [ ] No hidden global state
- [ ] Proper error handling
- [ ] Structured logging

### Database
- [ ] Constraints defined
- [ ] Foreign keys defined
- [ ] Required indexes added
- [ ] Migration reviewed
- [ ] Transaction boundaries defined
- [ ] Concurrency cases tested

### API
- [ ] Authentication
- [ ] Authorization
- [ ] Input validation
- [ ] Response schemas
- [ ] Pagination
- [ ] Correct status codes
- [ ] Idempotency where required

### Reliability
- [ ] Timeouts
- [ ] Safe retries
- [ ] Failure handling
- [ ] Graceful shutdown
- [ ] External-service failure scenarios tested

### Security
- [ ] Secrets externalized
- [ ] Passwords hashed
- [ ] Tokens protected
- [ ] File uploads validated
- [ ] Server-side authorization
- [ ] Sensitive data excluded from logs

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] API tests
- [ ] Critical E2E flows
- [ ] Race/concurrency tests where required
- [ ] Migration tests

### Operations
- [ ] Health endpoints
- [ ] Metrics
- [ ] Structured logs
- [ ] Tracing where appropriate
- [ ] Alerts
- [ ] Database backup strategy
- [ ] Dependency/security scanning

## Golden Rule

For every feature:

    1. Understand the business rule
    2. Define the domain model
    3. Define database constraints
    4. Define service/use-case behavior
    5. Define API contract
    6. Implement repository queries
    7. Implement service logic
    8. Implement router
    9. Add logging/observability
    10. Write unit tests
    11. Write integration/API tests
    12. Test failure and concurrency scenarios
    13. Create/review Alembic migration
    14. Run quality gates
    15. Review security and performance
    16. Deploy

Do not start by writing the endpoint. Start by defining the invariant and business behavior the endpoint must enforce.

## Engineering Standard

Prefer:

    Explicit > implicit
    Simple > clever
    Deterministic > magical
    Transactional > partially consistent
    Observable > opaque
    Testable > tightly coupled
    Secure-by-default > secure-by-convention
    Measured optimization > premature optimization
    Modular monolith > premature microservices

The objective is not maximum architecture. The objective is a backend where failures are predictable, data remains consistent, business rules are explicit, APIs are stable, security boundaries are clear, production behavior is observable, and changes can be made safely.
