from dataclasses import asdict, dataclass


@dataclass
class Filters:
    """Represents a set of optional filters for querying hydrological data.

    Each field corresponds to a filterable dimension of the dataset. Fields
    left as ``None`` are excluded from the query and treated as "no filter
    applied" for that dimension.

    Attributes:
        category: The category of the hydrological station or record
            (e.g. ``"Limnigráfica"``).
        department: The Colombian department where the station is located
            (e.g. ``"Antioquia"``).
        municipality: The municipality within the department where the
            station is located (e.g. ``"Medellín"``).
        status: The operational status of the station
            (e.g. ``"Activa"`` or ``"Suspendida"``).
        owner: The entity that owns or operates the station
            (e.g. ``"IDEAM"``).
        hydrographic_area: The broad hydrographic area that encompasses the
            station (e.g. ``"Magdalena - Cauca"``).
        hydrographic_zone: The hydrographic zone within the hydrographic area
            (e.g. ``"Alto Magdalena"``).
        hydrographic_subzone: The hydrographic subzone within the hydrographic
            zone (e.g. ``"Río Bogotá"``).
    """

    category: str | None = None
    department: str | None = None
    municipality: str | None = None
    status: str | None = None
    owner: str | None = None
    hydrographic_area: str | None = None
    hydrographic_zone: str | None = None
    hydrographic_subzone: str | None = None

    def to_dict(self) -> dict:
        """Converts the filters to a dictionary, omitting unset fields.

        Only fields whose value is not ``None`` are included in the result,
        making the output suitable for passing directly to query or API
        functions that interpret missing keys as "no filter applied".

        Returns:
            A dictionary mapping filter field names to their values for all
            fields that have been explicitly set (i.e. are not ``None``).
        """
        return {k: v for k, v in asdict(self).items() if v is not None}
