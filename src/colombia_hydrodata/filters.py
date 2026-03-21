from dataclasses import asdict, dataclass


@dataclass
class Filters:
    category: str | None = None
    department: str | None = None
    municipality: str | None = None
    status: str | None = None
    owner: str | None = None
    hydrographic_area: str | None = None
    hydrographic_zone: str | None = None
    hydrographic_subzone: str | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
