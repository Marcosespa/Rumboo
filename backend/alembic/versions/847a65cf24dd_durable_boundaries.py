"""Separar estado satelital y guardar trabajo y resultados recuperables."""
from alembic import op
import sqlalchemy as sa

revision = "847a65cf24dd"
down_revision = "5f22f636b715"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("consultas_satelitales", sa.Column("resultado", sa.JSON(), nullable=True))
    op.add_column("consultas_satelitales", sa.Column("viajes_solicitados", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("consultas_satelitales", sa.Column("intentos", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("consultas_satelitales", sa.Column("proximo_envio", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.add_column("consultas_satelitales", sa.Column("fallo_contado", sa.Boolean(), nullable=False, server_default=sa.false()))
    # Una consulta existente ya pudo haber sido enviada: conciliar antes de repetir POST.
    op.execute("UPDATE consultas_satelitales SET intentos = 1, fallo_contado = estado IN ('timeout', 'fallido')")
    for column in ("viajes_solicitados", "intentos", "proximo_envio", "fallo_contado"):
        op.alter_column("consultas_satelitales", column, server_default=None)
    op.create_table("vehiculos_satelitales",
        sa.Column("vehiculo_id", sa.Integer(), sa.ForeignKey("vehiculos.id"), primary_key=True),
        sa.Column("transportadora_id", sa.Integer(), sa.ForeignKey("transportadoras.id"), nullable=False),
        sa.Column("cuenta_satelital_id", sa.Integer(), sa.ForeignKey("cuentas_satelitales.id"), nullable=False),
        sa.Column("cuenta_version", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(200), nullable=False),
        sa.Column("device_id", sa.String(100), nullable=False),
        sa.Column("en_satelital", sa.Boolean(), nullable=True),
        sa.Column("ultima_posicion_id", sa.Integer(), sa.ForeignKey("posiciones.id"), nullable=True))
    op.create_index("ix_vehiculos_satelitales_transportadora_id", "vehiculos_satelitales", ["transportadora_id"])
    # Se conserva la ubicación histórica; referencias inválidas antiguas no se trasladan.
    op.execute("""INSERT INTO vehiculos_satelitales
        (vehiculo_id, transportadora_id, cuenta_satelital_id, cuenta_version, alias, device_id, en_satelital, ultima_posicion_id)
        SELECT v.id, v.transportadora_id, c.id, c.version, '', '', v.en_satelital, p.id
        FROM vehiculos v JOIN cuentas_satelitales c ON c.transportadora_id = v.transportadora_id
        LEFT JOIN posiciones p ON p.id = v.ultima_posicion_id AND p.vehiculo_id = v.id
            AND p.transportadora_id = v.transportadora_id""")
    op.drop_column("vehiculos", "ultima_posicion_id")
    op.drop_column("vehiculos", "en_satelital")
    op.create_table("entregas_pendientes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("transportadora_id", sa.Integer(), sa.ForeignKey("transportadoras.id"), nullable=False),
        sa.Column("evento", sa.String(100), nullable=False),
        sa.Column("destinatario", sa.String(100), nullable=False),
        sa.Column("clave", sa.String(200), nullable=False),
        sa.Column("datos", sa.JSON(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("intentos", sa.Integer(), nullable=False),
        sa.Column("proximo_intento", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reclamacion", sa.String(36), nullable=True),
        sa.Column("reclamada_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_codigo", sa.String(100), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("terminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("transportadora_id", "destinatario", "clave"))
    op.create_index("ix_entregas_estado_proximo", "entregas_pendientes", ["estado", "proximo_intento"])


def downgrade():
    op.add_column("vehiculos", sa.Column("en_satelital", sa.Boolean(), nullable=True))
    op.add_column("vehiculos", sa.Column("ultima_posicion_id", sa.Integer(), nullable=True))
    op.execute("""UPDATE vehiculos v SET en_satelital = s.en_satelital, ultima_posicion_id = s.ultima_posicion_id
        FROM vehiculos_satelitales s WHERE s.vehiculo_id = v.id""")
    op.drop_index("ix_entregas_estado_proximo", table_name="entregas_pendientes")
    op.drop_table("entregas_pendientes")
    op.drop_index("ix_vehiculos_satelitales_transportadora_id", table_name="vehiculos_satelitales")
    op.drop_table("vehiculos_satelitales")
    for column in ("fallo_contado", "proximo_envio", "intentos", "viajes_solicitados", "resultado"):
        op.drop_column("consultas_satelitales", column)
