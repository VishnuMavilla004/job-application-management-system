from django.db import models


class ApplicationStatus(models.TextChoices):
    APPLIED = "applied", "Applied"
    ASSESSMENT = "assessment", "Assessment"
    INTERVIEW = "interview", "Interview"
    OFFER = "offer", "Offer"
    REJECTED = "rejected", "Rejected"
    WITHDRAWN = "withdrawn", "Withdrawn"


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full Time"
    PART_TIME = "part_time", "Part Time"
    CONTRACT = "contract", "Contract"
    INTERNSHIP = "internship", "Internship"


class WorkMode(models.TextChoices):
    ONSITE = "onsite", "On-site"
    REMOTE = "remote", "Remote"
    HYBRID = "hybrid", "Hybrid"


class InterviewType(models.TextChoices):
    TECHNICAL = "technical", "Technical"
    HR = "hr", "HR"
    MANAGERIAL = "managerial", "Managerial"
    BEHAVIORAL = "behavioral", "Behavioral"
    OTHER = "other", "Other"


class InterviewOutcome(models.TextChoices):
    PENDING = "pending", "Pending"
    PASSED = "passed", "Passed"
    FAILED = "failed", "Failed"
    RESCHEDULED = "rescheduled", "Rescheduled"