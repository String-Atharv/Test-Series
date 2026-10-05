import enum

class UserRole(str,enum.Enum):
    ADMIN="admin"
    STUDENT="student"
    TEACHER="teacher"

class CACourses(str,enum.Enum):
    FOUNDATION="CA Foundation"
    INTERMEDIATE="CA Intermediate"
    FINAL="CA Final"

class QuestionType(str,enum.Enum):
    MCQ="mcq"
    THEORETICAL="theoretical"
    SHORT_ANSWER="short_answer"
    CASE_STUDY="case_study"
    NUMERICAL="numerical"
    
class Difficulty(str,enum.Enum):
    EASY="easy"
    HARD="hard"
    MEDIUM="medium"
    VERY_HARD="very_hard"
    VERY_EASY="very_easy"

class QuestionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class TestType(str,enum.Enum):
    MOCK_TEST="mock_test"
    PRACTICE_TEST="practice_test"
    TOPIC_TEST="topic_test"
    CHAPTER_TEST="chapter_test"
    UNIT_TEST="unit_test"
    FULL_SYLLABUS_TEST="full_syllabus_test"
    MCQ_TEST="mcq_test"
    CASE_STUDY_TEST="case_study_test"
    
class TestStatus(str,enum.Enum):
    DRAFT="draft"
    PUBLISHED="published"
    CLOSED="closed"
    UPCOMING="upcoming"
    
class TestAttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    EXPIRED = "expired"

class EvaluationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"