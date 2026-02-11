from pydantic import BaseModel, Field, ValidationError, model_validator
from enum import Enum
from datetime import datetime
from typing import List


class RankType(Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: RankType
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: List[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def validate_mission_rules(self) -> 'SpaceMission':
        if not self.mission_id.startswith("M"):
            raise ValueError('mission_id must start with \"M\"')

        cap_or_com_pres = False
        for e in self.crew:
            if e.rank == RankType.commander or e.rank == RankType.captain:
                cap_or_com_pres = True
        if cap_or_com_pres is False:
            raise ValueError('Must have at least one Commander or Captain')

        if self.duration_days > 365:
            experienced = sum(e.years_experience >= 5 for e in self.crew)
            if experienced / len(self.crew) < 0.5:
                raise ValueError('Long missions need 50% experienced crew')

        for e in self.crew:
            if e.is_active is False:
                raise ValueError('All crew members must be active.')
        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=========================================")

    sarah = CrewMember(
        member_id="CM_001",
        name="Sarah Connor",
        rank=RankType.commander,
        age="40",
        specialization="Mission Command",
        years_experience="15",
        is_active=True
    )
    john = CrewMember(
        member_id="CM_002",
        name="John Smith",
        rank=RankType.lieutenant,
        age="39",
        specialization="Navigation",
        years_experience="2",
        is_active=True
    )
    alice = CrewMember(
        member_id="CM_003",
        name="Alice Johnson",
        rank=RankType.officer,
        age="67",
        specialization="Engineering",
        years_experience="34",
        is_active=True
    )
    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date="2024-03-16T10:00:00",
        duration_days=900,
        budget_millions=2500.0,
        crew=[sarah, john, alice]
    )
    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew Members:")
    for e in mission.crew:
        print(f"- {e.name} ({e.rank.value} - {e.specialization})")
    print("\n=========================================")
    try:
        mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date="2024-03-16T10:00:00",
            duration_days=900,
            budget_millions=2500.0,
            crew=[john, alice],
        )
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()
