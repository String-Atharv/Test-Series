# CA Test Series Application — Functional Requirements

## 1. Overview

The CA Test Series application consists of a Student Web Application, Teacher Web Application, Admin capabilities, a FastAPI modular-monolith backend, PostgreSQL, and MinIO/S3-compatible object storage for PDFs.

### Actors

| Actor | Description |
|---|---|
| Student | Takes tests, uploads answer sheets, views evaluations and checked answer sheets, and may re-attempt tests. |
| Teacher | Creates/manages questions and tests, receives assigned submissions, evaluates answer sheets, provides feedback, and uploads checked answer sheets. |
| Admin | Manages users, curriculum, configuration, and administrative operations including reassignment. |

---

## 2. Authentication and Account Management

### FR-001 — Student Authentication
The system shall allow students to authenticate using Google Identity Services (GIS).

### FR-002 — Teacher Authentication
The system shall allow teachers to authenticate using Google Identity Services (GIS).

### FR-003 — Google Identity Verification
The backend shall verify the Google ID token before authenticating the application user. The Google `sub` claim shall be used as the immutable external identity identifier.

### FR-004 — Admin Authentication
The system shall allow administrators to authenticate using username/password credentials. Admin passwords shall use a secure password-hashing algorithm such as Argon2id.

### FR-005 — User Provisioning
Students and teachers shall not be able to create unrestricted application accounts themselves. Admins shall be able to provision, activate, deactivate, and manage accounts.

### FR-006 — User Status
Users shall support at least `ACTIVE` and `INACTIVE` status. Inactive users shall not access protected functionality.

### FR-007 — Role-Based Access
The system shall enforce authorization for `STUDENT`, `TEACHER`, and `ADMIN` roles.

---

## 3. Curriculum Management

### FR-008 — Course Management
Admins shall be able to create and manage CA courses such as Foundation, Intermediate, and Final.

### FR-009 — Subject Management
A course shall contain multiple subjects.

### FR-010 — Chapter Management
A subject shall contain multiple chapters.

### FR-011 — Topic Management
A chapter shall contain multiple topics.

### FR-012 — Curriculum Hierarchy
The hierarchy shall be:

```text
Course → Subject → Chapter → Topic
```

A topic shall belong to exactly one chapter.

### FR-013 — Display Ordering
Courses, subjects, chapters, and topics shall support configurable sibling display ordering.

---

## 4. Question Bank

### FR-014 — Question Creation
Authorized teachers shall be able to create questions.

Supported types shall include `MCQ`, `NUMERICAL`, `DESCRIPTIVE`, `CASE_STUDY`, and `TRUE_FALSE`.

### FR-015 — Question Attributes
A question shall support question text, type, difficulty, marks, correct answer where applicable, model answer where applicable, explanation where applicable, status, creator, and timestamps.

### FR-016 — Question Lifecycle
Questions shall support `DRAFT`, `ACTIVE`, and `ARCHIVED` states.

- **DRAFT:** being prepared and unavailable for normal test usage.
- **ACTIVE:** available for inclusion in new tests.
- **ARCHIVED:** preserved historically but unavailable for new tests.

### FR-017 — Question Topic Mapping
A question may belong to multiple topics through a many-to-many relationship.

### FR-018 — Question Search and Filtering
Teachers and admins shall be able to search/filter questions by attributes such as type, difficulty, status, topic, and creator.

### FR-019 — Question Editing
Authorized users shall be able to edit questions. Historical published test/question-paper content shall not be unexpectedly changed by later question-bank edits.

---

## 5. Test Management

### FR-020 — Test Creation
Authorized teachers shall be able to create tests with name, description, price if applicable, test type, status, maximum attempts, submission window, correction window, maximum replacements, evaluation window, publication timestamp, and audit timestamps.

### FR-021 — Test Types
The system shall support at least `PRACTICE`, `UNIT_TEST`, `MOCK_TEST`, `REVISION`, and `PREVIOUS_YEAR`.

### FR-022 — Test Lifecycle
Tests shall support `DRAFT`, `PUBLISHED`, and `CLOSED` states.

### FR-023 — Teacher Collaboration
A test may have multiple teachers, and a teacher may work on multiple tests. This shall be represented as a many-to-many relationship.

### FR-024 — Test Question Assignment
Authorized teachers shall be able to add question-bank questions to a test.

### FR-025 — Question Ordering
Each test question shall have a unique question number within that test.

### FR-026 — Test Publication
Only authorized users shall publish tests. The system shall prevent invalid/incomplete tests from being published.

---

## 6. Question Paper Management

### FR-027 — Question Paper Generation
The system shall generate a question paper from the questions assigned to a test, ordered by question number.

### FR-028 — Question Paper Storage
Question papers shall be stored in MinIO/S3-compatible object storage. PostgreSQL shall store document metadata and the storage key.

### FR-029 — Question Paper Integrity
Once a test is published, its issued question paper shall preserve the question content associated with that published test.

### FR-030 — Student Access
Eligible students shall be able to view/download the question paper for a published test.

---

## 7. Test Attempt Management

### FR-031 — Attempt Creation
When a student first accesses a test/question paper, the system shall create a test attempt if an active attempt does not already exist.

### FR-032 — Attempt Number
Attempts shall be sequentially numbered per student/test, with `(test_id, student_id, attempt_number)` unique.

### FR-033 — Maximum Attempts
The configured maximum attempt count shall be enforced.

### FR-034 — Attempt Status
Attempts shall support at least `IN_PROGRESS`, `SUBMITTED`, `COMPLETED`, and `EXPIRED`.

### FR-035 — First Access Timestamp
The system shall record the first question-paper/test access timestamp.

### FR-036 — Submission Deadline
The system shall calculate/store the deadline for the first confirmed answer-sheet submission. The default business rule is 12 months from first access.

### FR-037 — Server-Side Time
Eligibility, deadlines, and expiry shall use server-side timestamps. Client-provided timestamps shall not determine eligibility.

---

## 8. Answer Sheet Submission

### FR-038 — Answer Sheet Upload
Students shall be able to upload an answer-sheet PDF for an active attempt.

### FR-039 — File Validation
The system shall validate file type, size, and appropriate file-content/security constraints. Client-provided filename/MIME type alone shall not be trusted.

### FR-040 — Preview
The student shall preview the uploaded answer sheet before final confirmation.

### FR-041 — Submission Confirmation
The student shall explicitly confirm **Submit for Evaluation**. Uploading a file alone shall not constitute a confirmed submission.

### FR-042 — First Submission
The first confirmed submission shall mark the attempt as submitted, record the submission time, and start the correction window.

### FR-043 — Correction Window
The student may replace the answer sheet during the configured correction window. Default: 6 hours from first confirmed submission.

### FR-044 — Replacement Limit
The default maximum is 3 replacements. Therefore, the initial submission plus 3 replacements results in at most 4 uploaded versions.

### FR-045 — Replacement Does Not Create Attempt
Replacing an answer sheet shall not create a new test attempt.

### FR-046 — Submission Lock
After the correction deadline expires, answer-sheet replacement shall be rejected.

### FR-047 — Idempotent Submission
Retries or duplicate client requests shall not create duplicate logical submissions.

### FR-048 — Deadline Enforcement
A first submission after the configured submission deadline shall be rejected.

---

## 9. Evaluation Assignment and Teacher Distribution

### FR-049 — One Teacher per Evaluation
Each confirmed submission shall be assigned to exactly one teacher for evaluation. The assignment shall be represented by `evaluations.teacher_id`; `submissions` shall not duplicate `teacher_id`.

### FR-050 — Teacher Workload
A teacher may receive and evaluate multiple submissions.

### FR-051 — Teacher Selection
The distribution mechanism may consider teacher eligibility, workload, subject/test permissions, and availability.

### FR-052 — Evaluation Deadline
Each evaluation shall have an evaluation deadline based on the configured evaluation window.

### FR-053 — Teacher Work Queue
Teachers shall be able to view their assigned evaluations and filter by pending, in-progress, completed, and overdue work.

### FR-054 — Overdue Evaluation
The system shall identify evaluations whose deadline has passed while they remain incomplete.

### FR-055 — Administrative Reassignment
Admins shall be able to reassign an evaluation to another eligible teacher. Detailed assignment history and automatic reassignment may be added later.

---

## 10. Evaluation

### FR-056 — Evaluation Creation
An evaluation shall belong to exactly one submission. A submission shall have at most one evaluation record.

### FR-057 — Evaluation Teacher
Each evaluation shall reference exactly one teacher.

### FR-058 — Evaluation Status
Evaluations shall support at least `PENDING`, `IN_PROGRESS`, and `COMPLETED`. Overdue can be derived from deadline plus status.

### FR-059 — Answer Sheet Review
The assigned teacher shall be able to view/download the student's answer sheet.

### FR-060 — Question-Level Evaluation
The teacher shall provide marks and optional feedback for individual questions.

### FR-061 — Question Evaluation Uniqueness
Each question shall have at most one question-evaluation record within a given evaluation.

### FR-062 — Overall Feedback
The teacher shall be able to provide overall feedback.

### FR-063 — Evaluation Completion
The teacher shall explicitly complete the evaluation and the system shall record the completion timestamp.

### FR-064 — Marks Calculation
The system shall be able to calculate total marks from question-level marks. A separate persisted result table is not required initially.

---

## 11. Checked Answer Sheet

### FR-065 — Upload Checked Answer Sheet
The teacher shall be able to upload the checked/annotated answer sheet.

### FR-066 — Association
The checked answer sheet shall belong to the corresponding evaluation.

### FR-067 — Storage
Checked answer sheets shall be stored in MinIO/S3-compatible object storage, with metadata/storage key in PostgreSQL.

### FR-068 — Student Access
After evaluation completion, students shall be able to view/download the checked answer sheet.

### FR-069 — Evaluation Result Access
Students shall be able to view marks, question-level feedback, overall feedback, evaluation status, and the checked answer sheet when available.

---

## 12. Re-Attempts

### FR-070 — Re-Attempt
A student may intentionally re-attempt a test when the maximum-attempt policy permits it.

### FR-071 — New Attempt Record
A re-attempt shall create a new `test_attempts` record and shall not modify the previous attempt.

### FR-072 — New Submission Window
A new attempt shall receive its own submission deadline according to the configured policy.

### FR-073 — Historical Attempts
Previous attempts, submissions, evaluations, marks, feedback, and documents shall remain available as historical records.

---

## 13. Historical Integrity

### FR-074 — Attempt History
Previous attempts shall never be overwritten by later attempts.

### FR-075 — Submission History
Submission records shall remain linked to their original attempt.

### FR-076 — Evaluation History
Completed evaluations shall remain accessible after subsequent attempts.

### FR-077 — Document Integrity
Historical question papers, answer sheets, and checked answer sheets shall remain associated with their original test/attempt/evaluation.

---

## 14. Authorization and Security

### FR-078 — Student Authorization
Students shall only access their own attempts, submissions, evaluations, and checked answer sheets.

### FR-079 — Teacher Authorization
Teachers shall only evaluate submissions assigned to them unless an authorized administrative action permits otherwise.

### FR-080 — Admin Authorization
Administrative functions shall be restricted to authorized administrators.

### FR-081 — Object Storage Authorization
Documents shall not be exposed through unrestricted public object-storage URLs.

### FR-082 — Secure Document Access
The backend shall authorize the requesting user before generating a document download/view URL or streaming a document.

---

## 15. Search, Filtering, and Pagination

### FR-083 — Question Search
The question bank shall support search/filter operations.

### FR-084 — Test Search
Teachers/admins shall be able to search/filter tests.

### FR-085 — Teacher Queue Filtering
Teachers shall be able to filter evaluations by status, deadline, test, and other relevant attributes.

### FR-086 — Pagination
Large collections shall support server-side pagination, including questions, tests, submissions, evaluations, and users.

---

## 16. Notifications

### FR-087 — Assignment Notification
The system may notify teachers when new evaluations are assigned.

### FR-088 — Deadline Notification
The system may notify teachers when an evaluation deadline is approaching.

### FR-089 — Overdue Notification
The system may notify admins when evaluations become overdue.

### FR-090 — Completion Notification
The system may notify students when their evaluation is completed.

These notification capabilities may be implemented in a later phase.

---

## 17. Auditability

### FR-091 — Important Action Tracking
The system should record important administrative/workflow actions such as user activation, test publication, teacher assignment, evaluation completion, and reassignment.

### FR-092 — Timestamp Tracking
Important entities shall maintain appropriate creation/update timestamps and workflow timestamps such as first access, submission, correction deadline, assignment, and evaluation completion.

---

## 18. Business Rules Summary

| Rule | Default |
|---|---|
| Student/Teacher authentication | Google |
| Admin authentication | Username/password |
| Submission window | 12 months |
| Correction window | 6 hours |
| Maximum replacements | 3 |
| Maximum uploaded versions | 4 including initial submission |
| Submission → Teacher | Through `evaluation.teacher_id`; exactly 1 |
| Teacher → Evaluations | 1:N |
| Submission → Evaluation | 1:1 |
| Evaluation → Teacher | N:1 |
| Evaluation → Question Evaluations | 1:N |
| Test → Question Paper | 1:1 |
| Test → Teachers | M:N |
| Test → Questions | M:N |
| Question → Topics | M:N |
| Course → Subjects | 1:N |
| Subject → Chapters | 1:N |
| Chapter → Topics | 1:N |

---

## 19. End-to-End Workflows

### Workflow A — Teacher Creates a Test

```text
Teacher
  ↓
Create Test
  ↓
Add/Select Questions
  ↓
Order Questions
  ↓
Generate Question Paper
  ↓
Review
  ↓
Publish
  ↓
Available to Students
```

### Workflow B — Student Takes a Test

```text
Student
  ↓
Access Test
  ↓
Test Attempt Created
  ↓
Question Paper Available
  ↓
Student Solves Independently
  ↓
Upload Answer PDF
  ↓
Preview
  ↓
Confirm Submission
  ↓
6-Hour Correction Window
  ↓
Optional Replacement(s)
  ↓
Submission Locked
```

### Workflow C — Teacher Evaluation

```text
Confirmed Submission
        ↓
Evaluation Created
        ↓
Teacher Assigned
        ↓
Teacher Work Queue
        ↓
Teacher Opens Answer Sheet
        ↓
Evaluate Questions
        ↓
Add Feedback
        ↓
Upload Checked Answer Sheet
        ↓
Complete Evaluation
        ↓
Student Can View Result
```

### Workflow D — Student Re-Attempt

```text
Evaluation Completed
        ↓
Student Chooses Re-Attempt
        ↓
New Test Attempt
        ↓
New Submission Window
        ↓
New Answer Submission
        ↓
New Evaluation
```

---

## 20. V1 Scope Decisions

The initial version intentionally excludes:

- Microservices
- Separate question-bank database
- Separate evaluation-assignment entity
- Multiple simultaneous teachers evaluating one submission
- Automatic teacher reassignment
- Detailed assignment-history entity
- Timed online examination mode
- Teacher-requested reopening of locked submissions
- Generic document/file entity
- Separate persisted result table when totals can be derived

These may be introduced later if a concrete business requirement justifies them.

---

## 21. Core V1 Relationship Model

```text
User
 ├── Student
 ├── Teacher
 └── Admin

Course
  └── Subject
       └── Chapter
            └── Topic

Question
  └── QuestionTopic ─── Topic

Test
  ├── TestTeacher ─── Teacher
  ├── TestQuestion ─── Question
  └── QuestionPaper

Student
  └── TestAttempt
       └── Submission
            └── Evaluation
                 ├── Teacher
                 ├── QuestionEvaluation
                 │     └── Question
                 └── CheckedAnswerSheet
```

### Evaluation Ownership

```text
Submission
    │
    │ 1:1
    ▼
Evaluation
    │
    └──── N:1 ──── Teacher
```

Therefore, `teacher_id` is stored in `evaluations`, not duplicated in `submissions`.
