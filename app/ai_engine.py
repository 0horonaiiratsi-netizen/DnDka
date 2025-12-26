import random
from textwrap import dedent
from typing import List

from .models import Campaign, DMRequest, DMResponse, Message


class DMEngine:
    """A lightweight, offline-friendly Dungeon Master brain."""

    def __init__(self) -> None:
        self.scene_openers: List[str] = [
            "A cold mist curls at your feet as torches flicker along the ancient stone walls.",
            "The night sky crackles with distant lightning while tavern chatter hushes to a tense murmur.",
            "Sunlight filters through cracked cathedral glass, painting the floor in prismatic shards.",
            "A low growl echoes from somewhere ahead, mixing with the whisper of turning gears in hidden rooms.",
            "Campfires hiss in the rain while distant drums echo from the treeline.",
            "You stand on a balcony overlooking a city of lights, where airships drift between towers.",
        ]
        self.danger_hooks: List[str] = [
            "You sense a trap ahead—perhaps a quick perception check could help?",
            "A shadow detaches from the wall; you may want to ready an action or negotiate.",
            "Footsteps approach in rhythm with your heartbeat; stealth or bravado could change everything.",
            "There is a riddle etched nearby. Solving it might reveal loot, or a curse.",
            "A magical pulse distorts sound; arcana or investigation might dispel it.",
            "Supplies run low; a risky foraging attempt or a barter could sway survival.",
        ]
        self.support_hooks: List[str] = [
            "Remember your bonds and ideals; they can shape the world here.",
            "NPCs react to kindness as much as intimidation—try roleplay to shift the scene.",
            "Downtime actions can stabilize the party before the next challenge.",
            "Describe how you assist an ally to unlock advantage on their next roll.",
            "Use the environment: chandeliers, loose stones, rushing water—all tools for improvisation.",
            "Consider revealing a flaw or secret to earn inspiration or sway an NPC.",
        ]
        self.complication_tags: List[str] = [
            "timed event",
            "moral dilemma",
            "social intrigue",
            "environmental hazard",
            "puzzle gating",
            "resource scarcity",
        ]

    def generate_dm_entry(self, campaign: Campaign, request: DMRequest, author: str = "DM") -> Message:
        response = self.generate_response(campaign, request)
        return Message(author=author, text=response.reply)

    def generate_response(self, campaign: Campaign, request: DMRequest) -> DMResponse:
        opener = random.choice(self.scene_openers)
        danger = random.choice(self.danger_hooks)
        support = random.choice(self.support_hooks)
        complication = random.choice(self.complication_tags)

        players = ", ".join([p.character_name for p in campaign.players]) or "the party"
        campaign_context = dedent(
            f"""
            Campaign: {campaign.title}
            Tone: {campaign.tone}
            Setting: {campaign.setting}
            Summary: {campaign.summary}
            Characters: {players}
            Recent prompt: {request.prompt}
            Player-provided state: {request.campaign_state or 'n/a'}
            """
        ).strip()

        narrative = (
            f"{opener} In this {campaign.tone} tale set in {campaign.setting}, "
            f"{players} stand at the edge of a pivotal choice. {request.prompt.strip()} "
            f"Your actions ripple across the land. {danger}"
        )

        guidance = (
            f"Consider scene framing based on: {campaign_context}. "
            f"Try encouraging skill checks, exploration choices, or creative teamwork. {support} "
            f"Complication to feature: {complication}."
        )

        return DMResponse(reply=narrative, guidance=guidance)
