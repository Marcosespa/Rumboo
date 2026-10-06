from datetime import datetime, timezone

import pytest

from app.crawler import CrawlerSession, extract_vehicle, parse_reported_at, plate_from_alias


@pytest.mark.parametrize("alias, plate", [
    ("ABC123", "ABC123"),
    ("abc-123", "ABC123"),
    ("ABC 123 Juan Pérez", "ABC123"),
    ("Tracto SNE742", "SNE742"),
    ("Camión de Juan", "CAMIÓNDEJUAN"),
])
def test_placa_desde_alias(alias, plate):
    assert plate_from_alias(alias) == plate


@pytest.mark.parametrize("raw, expected", [
    ("05/10/2026 09:02:00", datetime(2026, 10, 5, 14, 2, tzinfo=timezone.utc)),
    ("05/10/2026 09:02", datetime(2026, 10, 5, 14, 2, tzinfo=timezone.utc)),
    ("Último reporte: 05/10/2026 09:02:00 PM", datetime(2026, 10, 6, 2, 2, tzinfo=timezone.utc)),
    ("2026-10-05T14:02:00Z", datetime(2026, 10, 5, 14, 2, tzinfo=timezone.utc)),
    ("No disponible", None),
    ("", None),
])
def test_fecha_del_reporte_a_utc(raw, expected):
    assert parse_reported_at(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("Hoy, 09:45:15 am", datetime(2026, 10, 6, 14, 45, 15, tzinfo=timezone.utc)),
    ("Ayer, 09:45:15 p. m.", datetime(2026, 10, 6, 2, 45, 15, tzinfo=timezone.utc)),
    ("Hace 10 s", None),
])
def test_fecha_absoluta_del_tooltip_sin_estimar_hace(raw, expected):
    assert parse_reported_at(raw, now=datetime(2026, 10, 6, 15, tzinfo=timezone.utc)) == expected


class Element:
    def __init__(self, text="", attrs=None, selectors=None):
        self.text, self.attrs, self.selectors = text, attrs or {}, selectors or {}

    def get_attribute(self, name):
        return self.attrs.get(name, "")

    def find_elements(self, by, selector):
        return self.selectors.get(selector, [])

    def click(self):
        pass

    def is_displayed(self):
        return True


def test_extraer_ficha_incluye_velocidad_cero_y_hora_utc():
    card = Element(selectors={
        "iw-vehicle-serviceCode": [Element(attrs={"textContent": "ABC123"})],
        "#iwv-position-value": [Element("4.6, -74.1")],
        "#iwv-speed-value": [Element("0 km/h")],
        "#iwv-state-value-txt": [Element("Detenido")],
        "#iw-vehicle-text": [Element("Bogotá")],
        "iw-last-report-value": [Element(attrs={"textContent": "06/10/2026 09:45:15 am\nReporta cada: 1 minuto"})],
    })
    element = Element(attrs={"id": "ABC123"}, selectors={"[id$='_alias'] span": [Element("ABC123")]})
    driver = Element(selectors={"ABC123": [element], "iw-vehicle-map": [card]})
    crawler = CrawlerSession({})
    crawler.driver = driver
    row = crawler.read_details(element, extract_vehicle(element))
    assert (row["lat"], row["lng"], row["speed_kmh"]) == (4.6, -74.1, 0)
    assert row["status"] == "Detenido"
    assert row["reported_at"] == datetime(2026, 10, 6, 14, 45, 15, tzinfo=timezone.utc)
    assert row["device_id"] == ""  # el id DOM es la placa, no un dispositivo.


def test_coordenadas_cero_se_devuelven_nulas():
    element = Element(attrs={"id": "ABC123", "data-coords": "0,0"}, selectors={"[id$='_alias'] span": [Element("ABC123")]})
    row = extract_vehicle(element)
    assert row["lat"] is None and row["lng"] is None


def test_lista_virtualizada_recoge_todos_los_vehiculos(monkeypatch):
    class Driver(Element):
        def __init__(self):
            super().__init__()
            self.offset = 0
            self.viewport = Element()
            self.rows = [Element(attrs={"id": plate}, selectors={"[id$='_alias'] span": [Element(plate)]})
                         for plate in ("ABC123", "DEF456", "GHI789")]

        def find_elements(self, by, selector):
            if selector == "cdk_scroll_location_vehicles_list":
                return [self.viewport]
            if selector == "mat-expansion-panel-header":
                return [Element("3 vehículos")]
            if selector == "div.container-vehicle-list":
                return [self.rows[self.offset]]
            return [row for row in self.rows if row.get_attribute("id") == selector]

        def execute_script(self, script, viewport, *args):
            if "scrollTop = 0" in script:
                self.offset = 0
            elif "return arguments[0].scrollTop" in script:
                return self.offset
            else:
                self.offset += 1
                return self.offset < len(self.rows)

    monkeypatch.setattr("app.crawler.time.sleep", lambda delay: None)
    crawler = CrawlerSession({})
    crawler.driver = Driver()
    monkeypatch.setattr(crawler, "read_details", lambda element, row: row)
    assert [row["plate"] for row in crawler.read_fleet()] == ["ABC123", "DEF456", "GHI789"]
