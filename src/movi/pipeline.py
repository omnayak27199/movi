"""High-level episode pipeline scaffold."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PipelineStage:
    name: str
    implemented: bool
    description: str

STAGES = (
    PipelineStage("screenplay", False, "Expand the outline into a timed screenplay."),
    PipelineStage("voice", False, "Generate/record dialogue using approved voices."),
    PipelineStage("sound", False, "Create or license score, ambience, and Foley."),
    PipelineStage("visuals", False, "Generate shots with stable character references."),
    PipelineStage("assembly", False, "Compose assets into an editable episode cut."),
    PipelineStage("quality-check", False, "Check timing, audio, missing assets, and continuity."),
)

def status() -> list[PipelineStage]:
    """Return implementation status without implying unfinished work is complete."""
    return list(STAGES)
