"""normalize existing event locations

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-12 01:30:00.000000
"""

from alembic import op

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    replacements = {
        "Online": [
            "online",
            "ONLINE",
            "Online Etkinlik",
            "remote",
            "Remote",
            "Uzaktan",
            "Çevrimiçi",
            "cevrimici",
        ],
        "İstanbul": ["Istanbul", "ISTANBUL", "istanbul", "İSTANBUL"],
        "İzmir": ["Izmir", "IZMIR", "izmir", "İZMİR"],
        "Eskişehir": ["Eskisehir", "ESKISEHIR", "eskisehir", "ESKİŞEHİR"],
        "Elazığ": ["Elazig", "ELAZIG", "elazig", "ELAZIĞ"],
    }
    connection = op.get_bind()
    for canonical, variants in replacements.items():
        placeholders = ", ".join(f":value_{index}" for index in range(len(variants)))
        parameters = {f"value_{index}": value for index, value in enumerate(variants)}
        parameters["canonical"] = canonical
        connection.exec_driver_sql(
            f"UPDATE events SET location = :canonical WHERE trim(location) IN ({placeholders})",
            parameters,
        )
    connection.exec_driver_sql(
        "UPDATE events SET location = NULL WHERE trim(location) IN ('', '-')"
    )


def downgrade() -> None:
    # Canonical values cannot be losslessly converted back to their original spellings.
    pass
