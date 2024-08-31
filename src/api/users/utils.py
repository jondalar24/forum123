"""Some utilities for api.users."""


from flask import abort

from src.users.models import User

# value es una cadena que incluye el campo por el cual se quiere ordenar
# y el orden (ascendente o descendente), separados por una coma.
def parse_order_by(value: str) -> dict[str, str] | None:  # noqa: CFQ004
    """Parse arguments provided."""
    if not value:
        return abort(400, "empty argument value is not allowed")

    try:
        parameter, order = value.split(",")
    except ValueError:
        return abort(400, "failed parsing parameters provided")

    if parameter not in User.SORTING_FIELDS or order not in User.SORTING_ORDER:
        return abort(400, "provided value is not allowed")
    return {"field": parameter, "order": order}
