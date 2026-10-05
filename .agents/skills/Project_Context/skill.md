# CA Test Series — Project Context Skill

## 1. Project
A production-grade CA Test Series platform with:
- Student Web
- Teacher Web
- Admin capabilities
- One FastAPI modular-monolith backend
- PostgreSQL as relational source of truth
- MinIO locally / S3 in production for PDFs and documents

Primary goals: correctness, security, data integrity, resilience, observability, testability, maintainability, and safe schema evolution.

## 2. Architecture
Use:

Student Web ─┐
Teacher Web ─┼→ FastAPI Modular Monolith → PostgreSQL
Admin ───────┘                         └→ MinIO/S3

Do not introduce microservices without a concrete operational or organizational requirement.

Preferred backend flow:

Router → Service → Repository → SQLAlchemy → PostgreSQL

External integrations should be isolated behind clear services/interfaces.


## 4. Technology
- Python
- FastAPI
- Pydantic v2
- Pydantic Settings
- SQLAlchemy 2.x
- AsyncSession
- PostgreSQL
- Alembic
- pytest
- httpx
- Ruff
- mypy/pyright where useful
- Docker/Docker Compose

Authentication:
- Students/teachers: Google Identity Services; backend verifies ID token; use Google `sub` as stable external identity.
- Admin: username/password; store only Argon2id password hash.
- PostgreSQL is authoritative for role and account status.
- Never trust role/user identity supplied by clients.

## 5. Database
PostgreSQL stores:
- users
- curriculum
- questions
- test configuration
- test/question relationships
- teacher/test relationships
- attempts
- submission metadata
- evaluations
- question-level evaluation

MinIO/S3 stores:
- generated question papers
- student answer PDFs
- checked answer PDFs

Never store large PDFs in PostgreSQL unless a specific requirement justifies it.

Use SQLAlchemy ORM + Alembic. Never use `create_all()` as production schema management.

## 6. Current V1 Tables
- users
- ca_courses
- subjects
- chapters
- topics
- questions
- question_topics
- tests
- test_teachers
- test_questions
- question_papers
- test_attempts
- submissions
- evaluations
- question_evaluations

Potential future tables only when justified:
- submission_versions
- audit_logs
- notifications
- idempotency_records
- evaluation_documents

## 7. Curriculum
Hierarchy:

CA Course
→ Subject
→ Chapter
→ Topic

Relationships:
- Course 1:N Subject
- Subject 1:N Chapter
- Chapter 1:N Topic

Use `display_order` for sibling presentation order where required.

Typical uniqueness:
- unique(course_id, display_order)
- unique(subject_id, display_order)
- unique(chapter_id, display_order)

## 8. Question Bank
Questions belong in PostgreSQL.

Recommended fields:
- id
- question_text TEXT
- question_type
- difficulty
- marks
- correct_answer nullable
- model_answer nullable
- explanation nullable
- status
- created_by
- created_at
- updated_at

Question types:
- MCQ
- NUMERICAL
- DESCRIPTIVE
- CASE_STUDY
- TRUE_FALSE

Difficulty:
- EASY
- MEDIUM
- HARD

Question status:
- DRAFT: being prepared/reviewed
- ACTIVE: available for new tests
- ARCHIVED: unavailable for new tests but retained historically

Do not use question status for student attempt/evaluation state.

## 9. Question Topics
A question may cover multiple topics.

Use:
`question_topics(question_id, topic_id)`

Composite primary key:
`(question_id, topic_id)`

Do not add subject_id/chapter_id/topic_id directly to questions merely to represent the M:N relationship.

## 10. Tests
Recommended fields:
- id
- name
- description
- price nullable
- test_type
- status
- max_attempts
- submission_window_months
- correction_window_hours
- max_submission_replacements
- published_at nullable
- created_at
- updated_at

Test types:
- PRACTICE
- UNIT_TEST
- MOCK_TEST
- REVISION
- PREVIOUS_YEAR

Test status:
- DRAFT
- PUBLISHED
- CLOSED

Current workflow does not require `duration_minutes` because students may solve the paper independently within the submission window. Add it only if timed online exams become a real requirement.

## 11. Teacher/Test Relationship
A test can be associated with many teachers and a teacher can work on many tests.

Use:
`test_teachers(test_id, teacher_id, role, created_at)`

Composite primary key:
`(test_id, teacher_id)`

Possible roles:
- OWNER
- EDITOR
- REVIEWER

If V1 has identical permissions for all assigned teachers, omit role initially.

Never store multiple teacher IDs in comma-separated text or JSON.

## 12. Test Questions
Use:
`test_questions(test_id, question_id, question_number)`

Primary key:
`(test_id, question_id)`

Constraint:
`UNIQUE(test_id, question_number)`

This defines which questions are in the test and their order.

Do not add per-test marks unless marks can actually differ from the question-bank value.

## 13. Question Paper
`question_papers`:
- id
- test_id UNIQUE
- storage_key
- file_name
- file_type
- file_size
- created_at
- updated_at

Relationship:
`Test 1:1 QuestionPaper`

Generation:
Test Questions → order by question_number → generate PDF → store in MinIO/S3 → store metadata in PostgreSQL.

A published question paper should be treated as immutable so later question-bank changes cannot silently alter an already-issued paper.

## 14. Test Attempts
`test_attempts`:
- id
- test_id
- student_id
- attempt_number
- status
- question_paper_accessed_at
- answer_submission_deadline_at
- submitted_at nullable
- correction_deadline_at nullable
- submission_replacement_count
- created_at
- updated_at

Constraint:
`UNIQUE(test_id, student_id, attempt_number)`

Statuses:
- IN_PROGRESS
- SUBMITTED
- COMPLETED
- EXPIRED

Semantics:
- IN_PROGRESS: question paper accessed, no first confirmed submission
- SUBMITTED: first submission confirmed, correction window open
- COMPLETED: correction window closed and answer is locked
- EXPIRED: submission deadline passed without first valid submission

Evaluation status is separate from attempt status.

## 15. Attempt Timing
When the student first accesses the question paper:
- set `question_paper_accessed_at`
- calculate `answer_submission_deadline_at`

Current example:
`submission_window_months = 12`

When the first submission is confirmed:
- set `submitted_at`
- calculate `correction_deadline_at`

Current example:
`correction_window_hours = 6`

Current replacement policy:
`max_submission_replacements = 3`

These are configuration values, not hard-coded values scattered through code.

Use timezone-aware timestamps. Store absolute timestamps consistently in UTC. Do not trust client timestamps for enforcement.

## 16. Submissions
`submissions`:
- id
- attempt_id UNIQUE
- storage_key
- file_name
- file_type
- file_size
- submitted_at
- created_at
- updated_at

Relationship:
`TestAttempt 1:1 Submission`

V1 does not need `is_current` or `submission_no`.

The same submission row represents the currently valid answer PDF during the correction window.

If historical versions are required later, introduce `submission_versions`.

## 17. Submission Idempotency
Submission uploads are retry-sensitive.

Example:
`PUT /api/v1/student/attempts/{attempt_id}/submission`

Use an `Idempotency-Key`.

A repeated request with the same key must not consume replacement quota twice or create duplicate business effects.

Do not implement production idempotency using only process-local memory.

## 18. Submission Concurrency
Two simultaneous replacement requests must not both pass the replacement limit.

Use:
- transaction
- row-level locking / `SELECT FOR UPDATE`
- atomic updates
- appropriate isolation
- unique constraints where applicable

Python locks are not a distributed correctness mechanism.

## 19. Submission + Object Storage
PostgreSQL and S3/MinIO are separate systems.

Safe conceptual flow:
1. Authenticate
2. Authorize
3. Lock/check attempt
4. Validate deadline
5. Validate replacement quota
6. Validate file
7. Upload new object
8. Update DB metadata
9. Commit
10. Clean old object after successful commit

Never delete the old valid object first.

Design for partial failure and orphan-object reconciliation.

## 20. Evaluations
`evaluations`:
- id
- submission_id UNIQUE
- teacher_id
- status
- overall_feedback nullable
- evaluated_at nullable
- checked_storage_key nullable
- checked_file_name nullable
- checked_file_type nullable
- checked_file_size nullable
- checked_uploaded_at nullable
- created_at
- updated_at

Statuses:
- PENDING
- IN_PROGRESS
- COMPLETED

Relationship:
`Submission 1:1 Evaluation`

The teacher may upload a checked/annotated answer PDF.

## 21. Question-Level Evaluation
`question_evaluations`:
- id
- evaluation_id
- question_id
- marks_obtained
- feedback nullable
- created_at
- updated_at

Constraint:
`UNIQUE(evaluation_id, question_id)`

Do not add test_id because it is derivable:
question_evaluation → evaluation → submission → attempt → test.

Total marks can initially be derived with SUM; no separate results table is required for V1.

## 22. Document Ownership
Question Paper:
- belongs to Test
- generated by teacher/system workflow
- visible to students

Answer Sheet:
- belongs to Submission
- uploaded by student
- visible to authorized teacher

Checked Answer Sheet:
- belongs to Evaluation
- uploaded by teacher
- visible to student after evaluation

Avoid a generic file table in V1 unless several domains genuinely need the same abstraction.

## 23. API Design
Use `/api/v1/`.

Possible role-oriented paths:
- `/api/v1/student/...`
- `/api/v1/teacher/...`
- `/api/v1/admin/...`

Prefer business actions:
`POST /tests/{test_id}/publish`

over generic status mutation:
`PATCH /tests/{test_id} {"status":"PUBLISHED"}`

Routers should be thin. Services own business rules.

## 24. Service Layer
Services orchestrate use cases.

Examples:
- TestService
- QuestionService
- AttemptService
- SubmissionService
- EvaluationService

Services handle:
- business validation
- authorization decisions
- state transitions
- transaction orchestration
- repository calls
- external integration coordination

Do not make routers or repositories responsible for these rules.

## 25. Repository Layer
Repositories focus on persistence/query concerns.

Good examples:
- get_test()
- list_questions()
- create_question()
- get_attempt()
- update_submission()
- get_evaluation()

Repositories should not decide business rules such as whether a student may replace a submission.

Avoid committing inside every repository method.

## 26. State Machines
Test:
`DRAFT → PUBLISHED → CLOSED`

Attempt:
`IN_PROGRESS → SUBMITTED → COMPLETED`
or
`IN_PROGRESS → EXPIRED`

Evaluation:
`PENDING → IN_PROGRESS → COMPLETED`

Create explicit service methods:
- publish_test()
- submit_attempt()
- replace_submission()
- start_evaluation()
- complete_evaluation()

Validate current state before every transition.

## 27. Authorization
For protected actions verify:
1. authentication
2. role
3. resource permission
4. business state

Example:
Teacher modifies test:
- authenticated
- TEACHER role
- teacher has required relationship/role in `test_teachers`
- test is editable

Frontend protection is never sufficient.

## 28. Error Handling
Use domain/application exceptions such as:
- ResourceNotFoundError
- PermissionDeniedError
- ConflictError
- InvalidStateTransitionError
- SubmissionWindowExpiredError
- CorrectionWindowExpiredError
- ReplacementLimitExceededError
- IdempotencyConflictError

Map them at the API boundary.

Typical mapping:
- 401 unauthenticated
- 403 forbidden
- 404 not found
- 409 state/conflict
- 422 request validation
- 500 unexpected failure

Never expose stack traces, SQL errors, secrets, or internal implementation details.

## 29. Database Rules
Use PostgreSQL constraints for invariants wherever practical:
- unique email
- unique Google subject
- unique test/question
- unique question number within test
- unique attempt number per student/test
- unique submission per attempt
- unique evaluation per submission
- unique question evaluation per evaluation/question

Use foreign keys and explicit nullability.

Avoid redundant fields unless there is a demonstrated reason.

## 30. Transactions
A complete business operation should generally use one transaction.

Example publish flow:
- validate test
- authorize teacher
- validate questions
- verify question paper
- change status
- set published_at
- commit

If a required operation fails, roll back.

Do not perform long external operations while holding a DB transaction unless necessary.

## 31. Testing
Use:
- unit tests for business logic
- PostgreSQL integration tests for persistence/constraints
- API tests for HTTP/auth/validation
- E2E tests for critical journeys

Critical journey:
Teacher creates questions → creates test → assigns questions → generates paper → publishes → student accesses paper either by downloading or view online → attempt created → student submits by uploadinf answer pdf  → optional replacements → lock → teacher evaluates → checked PDF → student sees evaluation → optional re-attempt.

Test invalid transitions, duplicate requests, concurrency, deadline expiry, replacement limits, authorization failures, and partial storage failures.

## 32. Alembic
Workflow:
model change → migration → manually review → test migration → staging → deployment.

Never blindly trust autogenerated migrations.

For destructive/large changes use expand → migrate/backfill → contract.

## 33. Storage Security
Validate:
- file size
- MIME/content where practical
- filename
- authorization
- storage key

Never use raw user filenames as storage paths.

Use controlled keys such as:
- `question-papers/{test_id}/paper.pdf`
- `submissions/{attempt_id}/answer.pdf`
- `evaluations/{evaluation_id}/checked-answer.pdf`

Do not expose unrestricted object-storage access.

## 34. Observability
Use structured logs with useful context:
- request_id
- user_id when appropriate
- route
- method
- status
- duration
- error type

Never log passwords, access tokens, or sensitive document contents.

Track metrics for:
- request latency
- 4xx/5xx
- DB errors
- connection pool usage
- upload failures
- authentication failures
- evaluation failures

Use OpenTelemetry when tracing is useful.

Provide:
- `/health/live`
- `/health/ready`

## 35. Security
- Server-side authorization is mandatory.
- Passwords use Argon2id.
- Google tokens are verified server-side.
- Secrets come from configuration/secret management.
- SQL uses parameterization/ORM.
- Uploads are validated and size-limited.
- CORS is explicitly configured.
- HTTPS is required in production.
- Sensitive data is excluded from logs.
- Never trust client-provided role, user ID, timestamps, status, or ownership.

## 36. Performance
Avoid:
- N+1 queries
- unbounded collection endpoints
- `SELECT *` when unnecessary
- missing indexes
- huge response payloads
- unnecessary DB round trips

Use pagination and suitable SQLAlchemy loading strategies.

Do not introduce Redis or another database without a measured need.

## 37. Time and Dates
Use timezone-aware datetimes.

Store absolute timestamps consistently in UTC.

Deadline fields:
- question_paper_accessed_at
- answer_submission_deadline_at
- submitted_at
- correction_deadline_at
- evaluated_at

Use server/database time for enforcement.

## 38. Failure Scenarios
Every important operation should answer:
- What if PostgreSQL fails?
- What if S3 fails?
- What if the client retries?
- What if two requests arrive concurrently?
- What if the process crashes halfway through?
- What if an external service times out?
- What if the response is lost after success?

Design for partial failure, retry, recovery, and observability.

## 39. Development Sequence
For a new feature:
1. Understand requirement
2. Identify domain
3. Define invariants
4. Modify schema
5. Add DB constraints
6. Create/review migration
7. Define Pydantic schemas
8. Implement repository
9. Implement service/use case
10. Implement authorization
11. Implement router
12. Add observability
13. Add unit tests
14. Add integration/API tests
15. Test failure and concurrency cases
16. Run lint/type/test gates
17. Security review
18. Performance review
19. Deploy

Do not start with the endpoint. Start with the business invariant.

## 40. AI Coding Rules for This Project
When generating or modifying code:
1. Preserve the established ERD unless a requirement explicitly changes it.
2. Do not invent business requirements.
3. Do not introduce MongoDB/Redis/microservices without justification.
4. Keep business logic out of routers.
5. Keep persistence logic out of services where a repository boundary is useful.
6. Do not silently change semantics of deadlines, attempts, submissions, or evaluation.
7. Do not add redundant columns without explaining the invariant they serve.
8. Do not create destructive migrations without explicit approval.
9. Add tests for every new business rule.
10. Consider retries and concurrency for every write operation.
11. Treat external systems as unreliable.
12. Never trust client authorization information.
13. Keep secrets and sensitive information out of source and logs.
14. Prefer simple, explicit production-safe solutions.
15. Explain significant trade-offs rather than hiding them in generated code.

## 41. Current Business Policy
Current example configuration:
- submission window: 12 months
- correction window: 6 hours
- maximum submission replacements: 3
- maximum attempts: 2

These values are configurable test policies and must not be scattered as magic numbers.

## 42. Critical Semantic Distinctions
Do not confuse:
- `question_type`: kind of question
- `difficulty`: difficulty
- `question.status`: question-bank lifecycle
- `test.status`: test lifecycle
- `attempt.status`: student's assessment lifecycle
- `submission`: student's answer document
- `evaluation.status`: teacher evaluation lifecycle
- submission replacement: another PDF in the same attempt
- new attempt: a deliberate re-attempt after the previous assessment cycle

## 43. North Star
The target backend is:

Thin API
→ explicit services
→ reliable repositories
→ PostgreSQL source of truth
+ controlled object storage
→ observable, testable, recoverable production system.

Optimize for correctness and maintainability rather than maximum architectural complexity.
