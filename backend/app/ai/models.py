from dataclasses import dataclass, field


@dataclass
class AIScore:

    score: int = 0

    reasons: list[str] = field(
        default_factory=list
    )

    recommendation: str = "HOLD"

    confidence: int = 0