from src.ingestion.database import Session, Meeting
from datetime import datetime


def seed_meetings():
    session = Session()

    meetings = [
        Meeting(
            title="Engineering Sprint Review",
            date=datetime.utcnow(),
            transcript="Priya will fix the auth service by Friday. Arjun will rollback PR 892 if not done. Team decided to use feature flags for all auth changes. Mobile push notifications deferred to Sprint 15.",
            summary="Sprint review covering auth service latency spike and team action items.",
            action_items=[
                {"task": "Fix auth service latency",
                 "owner": "Priya", "due": "Friday"},
                {"task": "Rollback PR 892 if not fixed",
                 "owner": "Arjun", "due": "EOD"}
            ],
            decisions=[
                "Adopt feature flags for auth changes",
                "Defer mobile push to Sprint 15"
            ],
            risk_flags=[
                "Auth latency affecting 12% of logins",
                "SLO targets at risk if latency continues"
            ]
        ),
        Meeting(
            title="Product Planning Meeting",
            date=datetime.utcnow(),
            transcript="Team discussed Q2 roadmap. Sarah will lead the new dashboard feature. Budget for cloud infrastructure approved. Concern raised about hiring timeline slipping.",
            summary="Q2 planning meeting covering roadmap, budget approval and hiring concerns.",
            action_items=[
                {"task": "Lead dashboard feature",
                 "owner": "Sarah", "due": "Q2"},
                {"task": "Finalise hiring plan",
                 "owner": "HR", "due": "Next week"}
            ],
            decisions=[
                "Cloud infrastructure budget approved",
                "Dashboard feature prioritised for Q2"
            ],
            risk_flags=[
                "Hiring timeline may slip by 4 weeks",
                "Dashboard dependency on auth service fix"
            ]
        ),
        Meeting(
            title="Customer Support Weekly",
            date=datetime.utcnow(),
            transcript="Support tickets up 20% this week. Most issues related to login failures. John will create a FAQ doc. Escalation process needs updating urgently.",
            summary="Weekly support review showing increased ticket volume linked to auth issues.",
            action_items=[
                {"task": "Create login FAQ document",
                 "owner": "John", "due": "Wednesday"},
                {"task": "Update escalation process",
                 "owner": "Support Lead", "due": "This week"}
            ],
            decisions=[
                "FAQ document to be published on knowledge base",
                "Escalation SLA reduced from 4h to 2h"
            ],
            risk_flags=[
                "Support tickets up 20% — unsustainable",
                "Login failures causing customer churn risk"
            ]
        ),
    ]

    for meeting in meetings:
        existing = session.query(Meeting)\
                          .filter_by(title=meeting.title)\
                          .first()
        if existing:
            print(f"  → already exists: {meeting.title}")
        else:
            session.add(meeting)
            print(f"  ✓ saved: {meeting.title}")

    session.commit()
    session.close()
    print(f"\n✓ Seeding complete")


if __name__ == "__main__":
    print("Seeding database with sample meetings...\n")
    seed_meetings()