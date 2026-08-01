from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Callable, Dict, Optional


ReferenceFactory = Callable[[], dict]


def load_reference_journey() -> dict:
    """Load the versioned typed fixture; no product content is recreated here."""
    module = import_module("tests.test_family_care_end_to_end_reference")
    return module.build_reference_journey()


@dataclass
class FamilyCareReviewSession:
    """Ephemeral cursor over the existing deterministic reference journey."""

    reference_factory: ReferenceFactory = load_reference_journey
    step: int = 0

    def __post_init__(self) -> None:
        self._reference = self.reference_factory()
        self._validate()

    def advance(self) -> Dict[str, object]:
        if self.step < 6:
            # Rebuild through the existing services before exposing the next snapshot.
            self._reference = self.reference_factory()
            self._validate()
            self.step += 1
        return self.view()

    def reset(self) -> Dict[str, object]:
        self._reference = self.reference_factory()
        self._validate()
        self.step = 0
        return self.view()

    def view(self) -> Dict[str, object]:
        journey = self._journey()
        situation = journey.situation
        experience = self._experience(journey)
        completed = self.step - 1
        chain = self._source_chain(completed) if completed >= 0 else self._empty_chain()
        return {
            "case": {
                "title": "Pflegefall in der Familie – Referenzreise",
                "anonymized": True,
                "notice": "Anonymisierte, vollständig typisierte Testdaten",
                "step": self.step,
                "total_steps": 6,
            },
            "understanding": {
                "facts": _texts(situation.facts),
                "hypotheses": _texts(situation.hypotheses),
                "unknowns": _texts(situation.unknowns),
                "contradictions": _texts(situation.contradictions),
                "goals": _texts(situation.goals),
                "statements": tuple(item.text for item in situation.referenced_user_statements),
                "state_id": situation.understanding_state_id,
            },
            "guardian_view": {
                "summary": situation.triggering_statement.text,
                "known": _texts(situation.facts),
                "open": tuple(
                    _guardian_open_text(item.text)
                    for item in (
                        journey.essential_open_points
                        + journey.other_open_points
                        + journey.deferred_points
                    )
                ),
                "next_checks": tuple(
                    item.reason for item in situation.professional_reviews
                )
                + tuple(item.description for item in situation.organizational_steps),
                "involved": tuple(
                    {
                        "label": item.label,
                        "role": item.role,
                        "relationship": item.relationship,
                    }
                    for item in situation.people
                ),
                "progress": "Schritt {} von 6".format(self.step),
            },
            "cross_domain": {
                "contributions": tuple({"domain": item.domain.value, "entries": tuple(entry.text for entry in item.explicit_entries)} for item in situation.contributions),
                "dependencies": tuple(item.description for item in situation.dependencies),
                "open_points": tuple(item.text for item in journey.essential_open_points + journey.other_open_points),
                "deferred_points": tuple(item.text for item in journey.deferred_points),
                "answered_points": tuple(item.text for item in journey.answered_by_revision_points),
                "people": tuple({"label": item.label, "role": item.role, "relationship": item.relationship} for item in situation.people),
                "documents": tuple(item.storage_reference for item in situation.documents),
                "steps": tuple(item.description for item in situation.organizational_steps),
                "reviews": tuple(item.reason for item in situation.professional_reviews),
            },
            "conversation": {
                "turns": tuple({"question": item.question, "point_id": item.point_id} for item in journey.turns),
                "current_question": None if journey.current_question is None else journey.current_question.text,
                "current_gap": None if journey.current_open_point is None else journey.current_open_point.text,
                "prepared_answer": None if self.step >= 6 else self._reference["statements"][self.step + 1].text,
                "can_advance": self.step < 6,
            },
            "journey": {
                "status": journey.status.value,
                "heading": experience.status_heading,
                "description": experience.status_description,
                "allowed_actions": tuple(item.value for item in experience.allowed_actions),
                "boundaries": experience.professional_boundaries,
                "professional_review": None if journey.professional_review is None else {
                    "reviews": tuple(item.reason for item in journey.professional_review.professional_reviews),
                    "open": tuple(item.text for item in journey.professional_review.deferred_points),
                },
            },
            "source_chain": chain,
            "debug": {
                "journey_id": journey.journey_id,
                "situation_id": situation.situation_id,
                "state_hash": situation.understanding_state_hash,
                "experience_id": experience.experience_id,
            },
        }

    def _journey(self):
        return self._reference["journey"] if self.step == 6 else self._reference["journeys"][self.step]

    def _experience(self, journey):
        service = import_module("life_decisions.family_care").GuardianFamilyCareExperienceService()
        return service.present(journey)

    def _source_chain(self, index: int) -> Dict[str, object]:
        turn = self._reference["turns"][index]
        answer = self._reference["statements"][index + 1]
        proposal = self._reference["proposal_sets"][index].proposals[0]
        result = self._reference["resolution_results"][index]
        clarification = self._reference["clarifications"][index]
        return {
            "statement": answer.text,
            "understanding_element": proposal.operation.value_text,
            "open_point": self._reference["journeys"][index].current_open_point.text,
            "question": turn.question,
            "answer": answer.text,
            "proposal": proposal.operation.operation.value,
            "resolution": result.resolution.resolution_type.value,
            "revision": None if clarification.revision is None else tuple(change.operation.value for change in clarification.revision.changes),
            "updated_state": clarification.resulting_understanding_state_id,
        }

    @staticmethod
    def _empty_chain() -> Dict[str, Optional[str]]:
        return {key: None for key in ("statement", "understanding_element", "open_point", "question", "answer", "proposal", "resolution", "revision", "updated_state")}

    def _validate(self) -> None:
        if len(self._reference["journeys"]) != 6 or len(self._reference["turns"]) != 6:
            raise ValueError("reference journey must contain six controlled turns")


def _texts(items) -> tuple:
    return tuple(item.text for item in items)


def _guardian_open_text(text: str) -> str:
    """Use controlled display text without changing the referenced artifact."""
    if text == "Die bestehende Vertretungsgrundlage ist offen.":
        return "Es ist noch offen, wer Entscheidungen übernehmen darf, wenn die betroffene Person das selbst nicht kann."
    return text
