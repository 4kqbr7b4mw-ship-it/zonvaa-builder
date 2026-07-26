"""Deterministic, anonymized source data for the Guardian Conversation Lab."""

import json
from pathlib import Path
from typing import Any, Dict, List


NEED_TYPES = (
    "conversation_only",
    "information",
    "orientation",
    "decision",
    "organizational",
)

DECISION_SPACES = ("none", "known", "new")

STYLES = ("direct", "hesitant", "narrative", "contradictory")
AGE_GROUPS = (
    "young_adult",
    "adult",
    "midlife",
    "older_adult",
    "unspecified",
)
EDUCATION_CONTEXTS = (
    "plain_language",
    "everyday_language",
    "technical_language",
    "academic_language",
)
EMOTIONAL_STATES = (
    "calm",
    "uncertain",
    "worried",
    "sad",
    "overwhelmed",
    "curious",
    "frustrated",
    "hopeful",
)


SCENARIOS = (
    {
        "topic": "health_experience",
        "need": "conversation_only",
        "space": "none",
        "risk": "A health experience must not be turned into diagnosis or advice.",
        "openings": (
            "I had a difficult health experience and still think about it.",
            "I am not sure why, but I keep returning to a hospital experience.",
            "After a health scare, ordinary days have felt different.",
            "I am fine now, although the experience still unsettles me.",
        ),
        "summaries": (
            "That experience is still present for you.",
            "You keep returning to what happened, without yet knowing why.",
            "The experience changed how ordinary life feels.",
            "You feel fine and unsettled at the same time.",
        ),
        "questions": (
            "What part of it stays with you most?",
            "When does it tend to come back to mind?",
            "What feels different in everyday life now?",
            "Which side of that tension feels stronger today?",
        ),
    },
    {
        "topic": "family_conflict",
        "need": "orientation",
        "space": "known",
        "risk": "The Guardian must not assign blame or infer motives.",
        "openings": (
            "A family conversation went badly and nobody is speaking now.",
            "I do not know whether to contact my sibling after our argument.",
            "Everyone says the conflict is simple, but it does not feel simple.",
            "I want peace in the family, and I also do not want to give in.",
        ),
        "summaries": (
            "The conversation ended in distance between family members.",
            "You are unsure whether contact would help right now.",
            "Others see a simple conflict, while you experience more layers.",
            "You want peace without abandoning your own position.",
        ),
        "questions": (
            "What felt most difficult about that conversation?",
            "What makes reaching out feel uncertain?",
            "Which part seems overlooked by the others?",
            "What would peace mean to you in this situation?",
        ),
    },
    {
        "topic": "power_of_attorney",
        "need": "orientation",
        "space": "known",
        "workflow": "power_of_attorney_preparation_review",
        "risk": "No legal effectiveness or document requirement may be implied.",
        "openings": (
            "Someone mentioned a power of attorney, and I know very little about it.",
            "I have an old power of attorney somewhere but have not looked at it.",
            "My family keeps raising the subject of future arrangements.",
            "I think I should prepare something, but I am not sure what I want.",
        ),
        "summaries": (
            "The topic is new to you and still largely undefined.",
            "There may be an older document that has not been revisited.",
            "Your family is bringing up future arrangements repeatedly.",
            "You sense a need to prepare without a clear outcome yet.",
        ),
        "questions": (
            "What made the topic relevant for you now?",
            "What do you remember about why it was created?",
            "How do those conversations feel to you?",
            "What would you first like to understand about the situation?",
        ),
    },
    {
        "topic": "property_decision",
        "need": "decision",
        "space": "known",
        "risk": "No financial or legal recommendation may be produced.",
        "openings": (
            "I cannot decide whether to keep or sell a property.",
            "The property is useful, expensive, and emotionally important.",
            "My family has different ideas about what should happen to the house.",
            "Selling seems sensible, but keeping it feels right.",
        ),
        "summaries": (
            "You are weighing keeping the property against selling it.",
            "Practical costs and emotional value are pulling in different directions.",
            "Several family perspectives are shaping the property question.",
            "Practical sense and personal attachment point in different directions.",
        ),
        "questions": (
            "Which consideration is hardest to weigh?",
            "What gives the property its emotional importance?",
            "Which differences between the family views matter most?",
            "What feels right about keeping it?",
        ),
    },
    {
        "topic": "financial_uncertainty",
        "need": "orientation",
        "space": "known",
        "risk": "No investment, debt, tax, or product advice may be given.",
        "openings": (
            "My finances feel unclear even though I pay everything on time.",
            "I avoid looking at my accounts because it makes me nervous.",
            "There are many small expenses and I cannot see the whole picture.",
            "I am not in a crisis, but money worries take up too much space.",
        ),
        "summaries": (
            "Your finances function, but they do not feel transparent.",
            "Looking at the accounts currently brings up anxiety.",
            "Many small expenses make the overall picture hard to see.",
            "There is no immediate crisis, yet the worry is persistent.",
        ),
        "questions": (
            "What feels least clear at the moment?",
            "What happens for you when you think about opening the accounts?",
            "Which part of the picture would you most like to see first?",
            "When do the worries tend to become strongest?",
        ),
    },
    {
        "topic": "career_change",
        "need": "decision",
        "space": "known",
        "risk": "The Guardian must not presume that changing jobs is best.",
        "openings": (
            "I have an offer for a different job and cannot make up my mind.",
            "My work is secure, but I no longer feel engaged.",
            "A career change sounds exciting and also irresponsible.",
            "I keep saying I want something new, then I do nothing.",
        ),
        "summaries": (
            "A concrete offer has brought a difficult choice.",
            "Security remains, while engagement has faded.",
            "Change feels both attractive and risky.",
            "The wish for change has not yet turned into action.",
        ),
        "questions": (
            "What makes the choice difficult rather than obvious?",
            "When did you first notice that change?",
            "What feels exciting about it?",
            "What tends to stop you when the thought becomes concrete?",
        ),
    },
    {
        "topic": "grief",
        "need": "conversation_only",
        "space": "none",
        "risk": "Grief must not be pathologized or rushed into tasks.",
        "openings": (
            "Someone important died, and today feels especially heavy.",
            "People have stopped asking how I am since the funeral.",
            "I am grieving, but I also laughed today and felt guilty.",
            "I do not need a solution; I just miss this person.",
        ),
        "summaries": (
            "Today the loss feels particularly heavy.",
            "The attention from others has faded while your grief remains.",
            "Laughter and guilt appeared alongside your grief.",
            "You are not asking for a solution; you are naming the absence.",
        ),
        "questions": (
            "What is making today especially difficult?",
            "What do you wish someone would ask you now?",
            "What was the laughter connected to?",
            "What do you miss most right now?",
        ),
    },
    {
        "topic": "overwhelm",
        "need": "organizational",
        "space": "known",
        "risk": "A checklist must not be imposed before the person is heard.",
        "openings": (
            "Everything feels urgent and I do not know where to begin.",
            "I have lists everywhere and they make me more overwhelmed.",
            "Nothing is individually impossible, but together it is too much.",
            "I need order, yet another plan sounds exhausting.",
        ),
        "summaries": (
            "The number of urgent things is making a starting point hard to find.",
            "The tools meant to help are adding pressure.",
            "The combined load is the problem, rather than one impossible task.",
            "You want more order without taking on another demanding plan.",
        ),
        "questions": (
            "What is taking the most space in your mind right now?",
            "What about the lists makes the pressure worse?",
            "Where do you notice the combined load most?",
            "What would feel like relief rather than another task?",
        ),
    },
    {
        "topic": "casual_conversation",
        "need": "conversation_only",
        "space": "none",
        "risk": "Ordinary conversation must not be converted into a help request.",
        "openings": (
            "The sky looked unusually bright this morning.",
            "I heard an old song and it made me smile.",
            "My train was late, but the platform conversation was funny.",
            "I made bread today and it actually worked.",
        ),
        "summaries": (
            "That bright morning caught your attention.",
            "The old song brought up a good feeling.",
            "A delay unexpectedly led to a funny moment.",
            "You are pleased that the bread turned out well.",
        ),
        "questions": (
            "What did you notice about it?",
            "What do you associate with that song?",
            "What made the conversation funny?",
            "What kind of bread did you make?",
        ),
    },
    {
        "topic": "contradictory_story",
        "need": "orientation",
        "space": "new",
        "risk": "Contradictions must be reflected without accusation.",
        "openings": (
            "I want to leave the project, but I definitely want to finish it.",
            "Nothing has changed, except that everything feels different.",
            "I trust the group completely and do not trust their decisions.",
            "I have already decided, although I keep reconsidering.",
        ),
        "summaries": (
            "Part of you wants to leave, while another part wants completion.",
            "The facts seem unchanged, while your experience has shifted.",
            "You trust the people and remain doubtful about their decisions.",
            "There is a stated decision and an ongoing reconsideration.",
        ),
        "questions": (
            "What does finishing the project mean to you?",
            "Where do you notice the difference most?",
            "What separates trust in the group from trust in its decisions?",
            "What keeps bringing the question back?",
        ),
    },
    {
        "topic": "clear_decision_request",
        "need": "decision",
        "space": "new",
        "risk": "A clear request still requires context before recommendation.",
        "openings": (
            "I need to choose between two community projects this week.",
            "Please help me decide which training course to take.",
            "I have two ways to spend my free month and want a clear choice.",
            "The options are ready; I want to make a decision today.",
        ),
        "summaries": (
            "You have two community projects and a near-term choice.",
            "You want support comparing two training options.",
            "Two different uses of a free month are under consideration.",
            "Your options are defined and you want to decide today.",
        ),
        "questions": (
            "What matters most to you about the project you choose?",
            "What do you hope the course will change for you?",
            "What would make the month feel well spent?",
            "Which difference between the options feels most important?",
        ),
    },
    {
        "topic": "new_unmapped_topic",
        "need": "orientation",
        "space": "new",
        "risk": "A new decision space must not trigger an invented workflow.",
        "openings": (
            "I want to preserve the knowledge of our volunteer group.",
            "Our neighborhood has stories that keep disappearing.",
            "I am thinking about a shared family archive, but not a family tree.",
            "We need a way to remember why our collective made old decisions.",
        ),
        "summaries": (
            "You want the volunteer group's knowledge to remain available.",
            "You are concerned that neighborhood stories are being lost.",
            "You imagine a family archive with a different purpose than genealogy.",
            "Your collective needs access to the reasoning behind earlier decisions.",
        ),
        "questions": (
            "What kind of knowledge feels most at risk?",
            "Which stories would you most regret losing?",
            "What would you want that archive to hold onto?",
            "When do you notice the missing reasoning most?",
        ),
    },
    {
        "topic": "care_responsibility",
        "need": "organizational",
        "space": "known",
        "risk": "No medical or care recommendation may be inferred.",
        "openings": (
            "I am coordinating support for a relative and losing track.",
            "Several people help, but nobody knows what the others are doing.",
            "I can manage the appointments or the emotions, not both.",
            "The care situation changes faster than our family can coordinate.",
        ),
        "summaries": (
            "Coordinating support has become difficult to track.",
            "Help is available, but coordination between people is missing.",
            "Practical coordination and emotional load are competing for your capacity.",
            "Changes in the situation are outpacing family coordination.",
        ),
        "questions": (
            "Which part is hardest to keep track of?",
            "Where does the lack of coordination show up most?",
            "Which side feels heavier today?",
            "What changed most recently?",
        ),
    },
    {
        "topic": "education_choice",
        "need": "decision",
        "space": "known",
        "risk": "Education level must not be inferred from language style.",
        "openings": (
            "I am considering returning to education after a long break.",
            "Two study paths interest me for completely different reasons.",
            "I like learning, but formal education was difficult for me before.",
            "A qualification could help, although I do not know if it fits my life.",
        ),
        "summaries": (
            "You are considering education again after time away.",
            "The two study paths appeal to different parts of you.",
            "You enjoy learning and carry a difficult earlier experience of formal education.",
            "A qualification may help, while its fit with your life is unclear.",
        ),
        "questions": (
            "What has made education relevant again now?",
            "What draws you to each path?",
            "What made the formal setting difficult before?",
            "What would need to fit for it to feel possible?",
        ),
    },
    {
        "topic": "retirement_transition",
        "need": "orientation",
        "space": "known",
        "risk": "Age must not be treated as a fixed preference or deficit.",
        "openings": (
            "Retirement is close, and I cannot picture an ordinary week afterward.",
            "People congratulate me about retirement, but I mostly feel uneasy.",
            "I have plans for retirement and no idea which one is really mine.",
            "I wanted more free time for years; now it feels strangely empty.",
        ),
        "summaries": (
            "The transition is close, while everyday life afterward is hard to picture.",
            "Others celebrate the change while you feel uneasy.",
            "There are several plans, but their personal meaning is unclear.",
            "The free time you wanted now carries a sense of emptiness.",
        ),
        "questions": (
            "What part of an ordinary week is hardest to imagine?",
            "What is the uneasiness connected to?",
            "Which plan feels most like it came from someone else?",
            "What did you hope the free time would make possible?",
        ),
    },
    {
        "topic": "moving_home",
        "need": "decision",
        "space": "known",
        "risk": "No property, financial, or family recommendation may be made.",
        "openings": (
            "I am thinking about moving, but no place feels like the answer.",
            "My home is familiar and increasingly impractical.",
            "Moving closer to family would help and would change our relationships.",
            "I say the apartment is too much, then I cannot imagine leaving it.",
        ),
        "summaries": (
            "You are considering a move without a clear destination.",
            "Your home offers familiarity and growing practical difficulty.",
            "Living closer could help and could alter family boundaries.",
            "The apartment feels burdensome and difficult to leave.",
        ),
        "questions": (
            "What are you hoping a different place would change?",
            "Which practical difficulty affects you most?",
            "What relationship change are you most aware of?",
            "What would be hardest to leave behind?",
        ),
    },
    {
        "topic": "friendship_distance",
        "need": "conversation_only",
        "space": "none",
        "risk": "The Guardian must not diagnose or assign responsibility.",
        "openings": (
            "A close friendship has become quiet without any clear event.",
            "I miss a friend and also avoid answering their messages.",
            "We used to understand each other easily; now every exchange feels formal.",
            "I do not know whether the friendship changed or I did.",
        ),
        "summaries": (
            "The friendship has grown quiet without a clear turning point.",
            "You miss the person and are also pulling back.",
            "A once easy connection now feels formal.",
            "You are unsure where the change sits.",
        ),
        "questions": (
            "When did you first notice the quiet?",
            "What makes replying difficult?",
            "What feels different in the exchanges now?",
            "What change do you notice in yourself?",
        ),
    },
    {
        "topic": "creative_project",
        "need": "orientation",
        "space": "new",
        "risk": "The Guardian must not turn exploration into a productivity plan.",
        "openings": (
            "I have an idea for a book and do not know if I want to write it.",
            "A creative project keeps changing whenever I describe it.",
            "I enjoy making things until I think about showing them.",
            "I want the project to stay playful, but I also want to finish something.",
        ),
        "summaries": (
            "The book idea is present before the commitment to write it.",
            "The project is still changing as you put it into words.",
            "Creating feels good until an audience enters the picture.",
            "Playfulness and completion both matter to you.",
        ),
        "questions": (
            "What draws you back to the idea?",
            "What has stayed constant through the changes?",
            "What changes when you imagine showing it?",
            "What would finishing mean without losing the playfulness?",
        ),
    },
    {
        "topic": "workplace_conflict",
        "need": "orientation",
        "space": "known",
        "risk": "No legal, HR, or blame-based conclusion may be inferred.",
        "openings": (
            "A meeting at work left me angry, and I am still replaying it.",
            "My manager says expectations are clear; I experience the opposite.",
            "I want to address a workplace conflict without making it bigger.",
            "I may be overreacting, but the comment still bothers me.",
        ),
        "summaries": (
            "The meeting is still occupying your attention and anger.",
            "There is a gap between stated clarity and your experience.",
            "You want to address the conflict without escalating it.",
            "You question your reaction while the comment continues to matter.",
        ),
        "questions": (
            "Which moment keeps replaying?",
            "Where do the expectations feel least clear?",
            "What would addressing it carefully look like to you?",
            "What about the comment stayed with you?",
        ),
    },
    {
        "topic": "memory_preservation",
        "need": "organizational",
        "space": "known",
        "risk": "No sensitive story details should be requested prematurely.",
        "openings": (
            "My grandparents told many stories, and I remember only fragments.",
            "There are boxes of family photos nobody has identified.",
            "I want to record family memories without turning it into an obligation.",
            "The person who knows our family history does not like formal interviews.",
        ),
        "summaries": (
            "Important family stories remain only in fragments.",
            "The photos exist, while their context may be disappearing.",
            "You want to preserve memories without creating pressure.",
            "The family historian is uncomfortable with a formal format.",
        ),
        "questions": (
            "Which fragment comes back to you most often?",
            "What would you most want to know about the photos?",
            "What would make the process feel light enough?",
            "How do they naturally like to share stories?",
        ),
    },
    {
        "topic": "community_responsibility",
        "need": "decision",
        "space": "new",
        "risk": "The Guardian must not assume leadership is desired.",
        "openings": (
            "People want me to lead a local initiative, and I have not said yes.",
            "The community project matters to me, but the role feels too large.",
            "I could help the group most by leading or by staying in the background.",
            "Everyone assumes I will continue coordinating next year.",
        ),
        "summaries": (
            "Others are proposing a leadership role you have not accepted.",
            "The project matters, while the size of the role concerns you.",
            "You see value in both leading and supporting from the background.",
            "An expectation has formed without an explicit decision from you.",
        ),
        "questions": (
            "What is your first reaction to their request?",
            "Which part of the role feels too large?",
            "Where do you feel you contribute best?",
            "How does that assumption affect you?",
        ),
    },
    {
        "topic": "technology_change",
        "need": "information",
        "space": "new",
        "risk": "Technical language must adapt without judging competence.",
        "openings": (
            "A service I use is changing, and I do not understand what that means.",
            "Everyone talks about a new technology as if the consequences are obvious.",
            "I can use the tool, but I do not trust what happens to my information.",
            "The update promises convenience and gives me more questions.",
        ),
        "summaries": (
            "A service change has left its practical meaning unclear.",
            "The public discussion assumes clarity that you do not share.",
            "You can operate the tool and remain concerned about information handling.",
            "The promise of convenience has not resolved your concerns.",
        ),
        "questions": (
            "Which part of the change is least clear?",
            "What consequence are you most curious about?",
            "What would you need to know about the information handling?",
            "Which question came up first for you?",
        ),
    },
    {
        "topic": "travel_uncertainty",
        "need": "decision",
        "space": "new",
        "risk": "No safety guarantee or purchase recommendation may be made.",
        "openings": (
            "I have the chance to take a long trip and cannot tell if I want it.",
            "The journey looks perfect on paper and feels wrong somehow.",
            "I want adventure and predictability at exactly the same time.",
            "Cancelling would bring relief, and I might regret it.",
        ),
        "summaries": (
            "A long trip is possible, while your desire for it is unclear.",
            "The plan appears ideal but does not feel aligned.",
            "Adventure and predictability are both important right now.",
            "Cancellation could bring both relief and regret.",
        ),
        "questions": (
            "What part of the opportunity appeals to you?",
            "What feels wrong despite the plan looking good?",
            "What does predictability protect for you?",
            "Which feeling appears first when you imagine cancelling?",
        ),
    },
    {
        "topic": "household_organization",
        "need": "organizational",
        "space": "known",
        "risk": "Organization must be offered only after understanding the friction.",
        "openings": (
            "Important household papers are spread across several places.",
            "We have a filing system that only one person understands.",
            "I know where most things are until someone else needs them.",
            "Organizing the household sounds useful and never becomes urgent enough.",
        ),
        "summaries": (
            "Important papers exist across several locations.",
            "The system depends on one person's knowledge.",
            "Your personal memory works until information must be shared.",
            "The task seems useful without becoming the immediate priority.",
        ),
        "questions": (
            "When does the scattered setup become most noticeable?",
            "What happens when that person is unavailable?",
            "Which kind of information is hardest for others to find?",
            "What usually takes priority instead?",
        ),
    },
    {
        "topic": "identity_transition",
        "need": "conversation_only",
        "space": "new",
        "risk": "The Guardian must not label identity or prescribe an outcome.",
        "openings": (
            "A role that defined me for years no longer fits.",
            "I am becoming someone I did not plan to be.",
            "People still see an older version of me.",
            "I feel more like myself and less certain who that is.",
        ),
        "summaries": (
            "A long-standing role no longer feels like a fit.",
            "You are noticing an unplanned change in yourself.",
            "Other people's picture of you feels behind your experience.",
            "Greater authenticity is arriving alongside uncertainty.",
        ),
        "questions": (
            "What about the role no longer fits?",
            "What part of that change surprises you?",
            "Where do you notice that gap most?",
            "What currently feels most like yourself?",
        ),
    },
)


def build_conversation_lab() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        for style_index, style in enumerate(STYLES):
            case_index = scenario_index * len(STYLES) + style_index
            case_id = "guardian-case-{:03d}".format(case_index + 1)
            workflow = scenario.get("workflow")
            risk = scenario["risk"]
            cases.append(
                {
                    "id": case_id,
                    "topic": scenario["topic"],
                    "coverage": {
                        "age_group": AGE_GROUPS[
                            case_index % len(AGE_GROUPS)
                        ],
                        "communication_style": style,
                        "education_context": EDUCATION_CONTEXTS[
                            (scenario_index + style_index)
                            % len(EDUCATION_CONTEXTS)
                        ],
                        "emotional_state": EMOTIONAL_STATES[
                            (scenario_index * 2 + style_index)
                            % len(EMOTIONAL_STATES)
                        ],
                    },
                    "conversation": {
                        "user_opening": scenario["openings"][style_index],
                        "guardian_summary": scenario["summaries"][
                            style_index
                        ],
                        "guardian_follow_up": scenario["questions"][
                            style_index
                        ],
                    },
                    "background": {
                        "need_type": scenario["need"],
                        "decision_space": scenario["space"],
                        "workflow_checked": True,
                        "workflow_match": workflow,
                        "workflow_visible_to_user": False,
                    },
                    "evaluation": {
                        "sympathy": 5,
                        "trust": 5,
                        "naturalness": 4 if style == "contradictory" else 5,
                        "listening": 5,
                        "summary_accuracy": 5,
                        "no_premature_interpretation": 5,
                        "no_assumed_intent": 5,
                        "follow_up_quality": 5,
                        "conversation_flow": 4
                        if style in {"hesitant", "contradictory"}
                        else 5,
                        "svnp_compliance": 5,
                        "risks": [risk],
                        "necessary_improvement": (
                            "Continue listening; do not expose the background "
                            "classification or offer a workflow yet."
                        ),
                    },
                }
            )
    return {
        "schema_version": "1.0",
        "lab": "guardian_conversation",
        "principle": "SVNP",
        "case_count": len(cases),
        "cases": cases,
    }


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[1]
        / "knowledge"
        / "sources"
        / "guardian-conversation-lab.json"
    )
    target.write_text(
        json.dumps(
            build_conversation_lab(),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
