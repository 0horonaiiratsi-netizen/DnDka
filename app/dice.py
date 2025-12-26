import random
import re
from dataclasses import dataclass
from typing import List


dice_pattern = re.compile(r"^(?P<count>\d+)d(?P<sides>\d+)(?P<modifier>[+-]\d+)?$")


@dataclass
class DiceRoll:
    expression: str
    rolls: List[int]
    modifier: int

    @property
    def total(self) -> int:
        return sum(self.rolls) + self.modifier


class DiceError(ValueError):
    pass


def roll(expression: str) -> DiceRoll:
    cleaned = expression.lower().strip().replace(" ", "")
    match = dice_pattern.match(cleaned)
    if not match:
        raise DiceError("Dice expression must look like '2d6+1'.")

    count = int(match.group("count"))
    sides = int(match.group("sides"))
    modifier_text = match.group("modifier") or "0"
    modifier = int(modifier_text)

    if count <= 0 or sides <= 0:
        raise DiceError("Dice count and sides must be positive integers.")
    if count > 50:
        raise DiceError("Too many dice in one roll (max 50).")

    rolls = [random.randint(1, sides) for _ in range(count)]
    return DiceRoll(expression=cleaned, rolls=rolls, modifier=modifier)
