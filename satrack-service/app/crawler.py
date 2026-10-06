"""Selenium adapter preserving the original crawler's login and DOM selectors."""
import logging
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.errors import ProviderError

logger = logging.getLogger(__name__)
BOGOTA = ZoneInfo("America/Bogota")


def parse_reported_at(raw, now=None):
    text = str(raw or "").strip().split("Reporta cada:")[0].strip()
    text = re.sub(r"([ap])\s*\.\s*m\s*\.?", r"\1m", text, flags=re.I)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return (parsed if parsed.tzinfo else parsed.replace(tzinfo=BOGOTA)).astimezone(timezone.utc)
    except ValueError:
        pass
    match = re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?", text)
    if match:
        for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d/%m/%Y %I:%M:%S %p", "%d/%m/%Y %I:%M %p"):
            try:
                return datetime.strptime(match.group().upper(), fmt).replace(tzinfo=BOGOTA).astimezone(timezone.utc)
            except ValueError:
                pass
    relative = re.search(r"\b(Hoy|Ayer),?\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[ap]m)?)", text, re.I)
    if relative:
        local = (now or datetime.now(timezone.utc)).astimezone(BOGOTA)
        date = (local - timedelta(days=relative[1].lower() == "ayer")).strftime("%d/%m/%Y")
        return parse_reported_at(f"{date} {relative[2]}")
    return None


def first_text(element, selectors):
    for selector in selectors:
        found = element.find_elements(By.CSS_SELECTOR, selector)
        if found and found[0].text.strip():
            return found[0].text.strip()
    return ""


def plate_from_alias(alias):
    """El alias de Satrack es editable ("ABC 123", "ABC-123 Juan"): se busca la placa dentro del texto."""
    compact = re.sub(r"[\s-]", "", alias).upper()
    match = re.search(r"[A-Z]{3}\d{3}", compact)
    return match.group() if match else compact


def extract_vehicle(element):
    # Selectors and fallbacks come from the user's original crawler.py.
    vehicle_id = element.get_attribute("id") or ""
    alias = first_text(element, ("[id$='_alias'] span", ".row-header", ".text-alarm-black")) or vehicle_id
    plate = plate_from_alias(alias)
    if not plate:
        return None
    address = first_text(element, ("[id$='_address'] span", ".address-text"))
    coords = element.get_attribute("data-coords") or address
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*[,;]\s*(-?\d+(?:\.\d+)?)", coords)
    lat, lng = (float(match[1]), float(match[2])) if match else (None, None)
    if lat is not None and (not -90 <= lat <= 90 or not -180 <= lng <= 180 or (lat, lng) == (0, 0)):
        lat, lng = None, None
    icons = element.find_elements(By.CSS_SELECTOR, ".icon-status")
    classes = icons[0].get_attribute("class") if icons else ""
    state = next((c[5:] for c in classes.split() if c.startswith("icon-") and c != "icon-status"), "desconocido")
    modern_icons = element.find_elements(By.CSS_SELECTOR, "st-icon[id^='div_vehicle_state_icon_']")
    if modern_icons:
        state = {"st_move": "En movimiento", "st_stop": "Detenido"}.get(
            modern_icons[0].get_attribute("icon"), state)
    raw = first_text(element, ("[id$='_date']", ".last-report-time"))
    return {"plate": plate, "name": alias, "device_id": element.get_attribute("data-device-id") or "", "lat": lat, "lng": lng, "speed_kmh": None,
            "status": state, "address": address, "reported_at": parse_reported_at(raw), "reported_at_raw": raw}


def wait_until_stable(driver, max_s=10):
    """La lista se llena de forma asíncrona: espera a que el número de vehículos deje de cambiar."""
    previous, deadline = -1, time.monotonic() + max_s
    while time.monotonic() < deadline:
        current = len(driver.find_elements(By.CSS_SELECTOR, "div[class*='container-vehicle-list']"))
        if current == previous and current > 0:
            return
        previous = current
        time.sleep(1)


class CrawlerSession:
    def __init__(self, settings):
        self.settings = settings
        self.driver = None
        self.identity = None

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.driver = None
        self.identity = None

    def evidence(self, code):
        if not self.driver:
            return
        directory = Path(self.settings["data_dir"]) / "failures"
        directory.mkdir(parents=True, exist_ok=True)
        stamp = f"{time.time_ns()}-{code}"
        try:
            # Remove entered credentials from retained HTML before writing evidence.
            self.driver.execute_script("document.querySelectorAll('input').forEach(i => {i.value = ''; i.removeAttribute('value')})")
            self.driver.save_screenshot(str(directory / f"{stamp}.png"))
            (directory / f"{stamp}.html").write_text(self.driver.page_source)
        except Exception:
            logger.warning("No se pudo guardar evidencia %s", code)

    def read_details(self, element, row):
        """La ficha del mapa expone coordenadas, velocidad y fecha que la lista omite."""
        vehicle_id = element.get_attribute("id")

        def matching_card(driver):
            cards = driver.find_elements(By.ID, "iw-vehicle-map")
            for card in cards:
                codes = card.find_elements(By.ID, "iw-vehicle-serviceCode")
                if card.is_displayed() and codes and codes[0].get_attribute("textContent").strip() == vehicle_id:
                    return card
            return False

        card = None
        # La lista puede aparecer antes de que el mapa registre el clic inicial.
        for attempt in range(2):
            try:
                candidates = self.driver.find_elements(By.ID, vehicle_id)
                if not candidates:
                    break
                candidates[0].click()
                card = WebDriverWait(self.driver, 8).until(matching_card)
                break
            except Exception:
                continue
        if card is None:
            return row
        coords = first_text(card, ("#iwv-position-value",))
        match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*", coords)
        if match:
            lat, lng = float(match[1]), float(match[2])
            if -90 <= lat <= 90 and -180 <= lng <= 180 and (lat, lng) != (0, 0):
                row.update(lat=lat, lng=lng)
        speed = first_text(card, ("#iwv-speed-value",))
        match = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*km/h\s*", speed, re.I)
        if match:
            row["speed_kmh"] = float(match[1].replace(",", "."))
        row["status"] = first_text(card, ("#iwv-state-value-txt",)) or row["status"]
        row["address"] = first_text(card, ("#iw-vehicle-text",)) or row["address"]
        dates = card.find_elements(By.ID, "iw-last-report-value")
        if dates:
            raw = dates[0].get_attribute("textContent").split("Reporta cada:")[0].strip()
            row.update(reported_at_raw=raw, reported_at=parse_reported_at(raw))
        return row

    def read_fleet(self):
        rows = {}
        viewports = self.driver.find_elements(By.ID, "cdk_scroll_location_vehicles_list")
        viewport = viewports[0] if viewports else None
        if viewport:
            self.driver.execute_script("arguments[0].scrollTop = 0", viewport)
        headers = self.driver.find_elements(By.CSS_SELECTOR, "mat-expansion-panel-header")
        counts = [re.search(r"(\d+)\s+vehículos", header.text, re.I) for header in headers]
        expected = next((int(match[1]) for match in counts if match), None)
        if expected == 0:
            return []
        while True:
            before = self.driver.execute_script("return arguments[0].scrollTop", viewport) if viewport else 0
            ids = [e.get_attribute("id") for e in self.driver.find_elements(By.CSS_SELECTOR, "div.container-vehicle-list")]
            for vehicle_id in ids:
                if vehicle_id in rows:
                    continue
                elements = self.driver.find_elements(By.ID, vehicle_id)
                if not elements:
                    continue
                row = extract_vehicle(elements[0])
                if row:
                    rows[vehicle_id] = self.read_details(elements[0], row)
            if not viewport or (expected is not None and len(rows) >= expected):
                break
            moved = self.driver.execute_script("const e = arguments[0], previous = arguments[1]; e.scrollTop = previous + Math.max(1, e.clientHeight * .8); return e.scrollTop > previous", viewport, before)
            if not moved:
                break
            time.sleep(0.3)
        if not rows or (expected is not None and len(rows) < expected):
            raise ProviderError("PROVIDER_CHANGED", "No fue posible leer la flota completa de Satrack")
        return list(rows.values())

    def read(self, username, password):
        import hashlib
        identity = hashlib.sha256(f"{username}\0{password}".encode()).hexdigest()
        if self.identity != identity:
            self.close()
        try:
            if not self.driver:
                options = Options()
                if self.settings["headless"]:
                    options.add_argument("--headless=new")
                for flag in ("--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"):
                    options.add_argument(flag)
                # La lista de vehículos no necesita imágenes; el mapa de Satrack consume mucha memoria.
                options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
                if self.settings["chrome_binary"]:
                    options.binary_location = self.settings["chrome_binary"]
                service = Service(executable_path=self.settings["chromedriver_path"]) if self.settings["chromedriver_path"] else Service()
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.set_page_load_timeout(45)
                self.driver.set_script_timeout(15)
                self.driver.get("https://login.satrack.com/login")
            else:
                self.driver.refresh()
            WebDriverWait(self.driver, 30).until(lambda d: d.find_elements(By.ID, "txt_login_username") or d.find_elements(By.CSS_SELECTOR, "div.container-vehicle-list, #viewport_sidenav_vehicles"))
            if self.driver.find_elements(By.ID, "txt_login_username"):
                wait = WebDriverWait(self.driver, 30)
                user_input = wait.until(EC.visibility_of_element_located((By.ID, "txt_login_username")))
                user_input.clear()
                user_input.send_keys(username)
                password_input = self.driver.find_element(By.ID, "txt_login_password")
                password_input.clear()
                password_input.send_keys(password)
                wait.until(EC.element_to_be_clickable((By.ID, "btn_login_login"))).click()

            def loaded(driver):
                # El badge invisible de reCAPTCHA no es un desafío para el usuario.
                captcha = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='/bframe'], iframe[title*='challenge'], input[autocomplete='one-time-code']")
                if any(e.is_displayed() for e in captcha):
                    raise ProviderError("CAPTCHA_REQUIRED", "Satrack requiere captcha o verificación manual")
                errors = driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .login-error, #lbl_login_error")
                if any(e.is_displayed() and e.text.strip() for e in errors):
                    raise ProviderError("AUTH_FAILED", "Usuario o contraseña de Satrack incorrectos")
                return driver.find_elements(By.CSS_SELECTOR, "div.container-vehicle-list, #viewport_sidenav_vehicles")

            try:
                WebDriverWait(self.driver, 60).until(loaded)
            except ProviderError:
                raise
            except Exception:
                if self.driver.find_elements(By.ID, "txt_login_username"):
                    raise ProviderError("AUTH_FAILED", "No fue posible iniciar sesión en Satrack")
                raise ProviderError("PROVIDER_CHANGED", "La página de Satrack no tiene el formato esperado")
            self.identity = identity
            wait_until_stable(self.driver)
            return self.read_fleet()
        except ProviderError as exc:
            if exc.code in ("CAPTCHA_REQUIRED", "PROVIDER_CHANGED"):
                self.evidence(exc.code)
            self.close()
            raise
        except Exception:
            self.close()
            raise ProviderError("PROVIDER_UNAVAILABLE", "No fue posible consultar la plataforma Satrack")
