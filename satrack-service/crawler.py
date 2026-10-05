import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from typing import List, Dict, Optional, Callable

def scrape_vehiculos_satrack(username: str, password: str, headless: bool = False) -> List[Dict]:
    """
    Extrae información de vehículos desde Satrack usando Selenium.
    
    Args:
        username: Usuario de Satrack
        password: Contraseña de Satrack
        headless: Si True, ejecuta el navegador en modo headless
    
    Returns:
        List[Dict]: Lista de diccionarios con información de vehículos
        Cada diccionario contiene: placa, ubicacion, latitud, longitud, estado, fecha
    
    Raises:
        Exception: Si hay un error durante el scraping
    """
    driver = None
    vehiculos = []
    
    try:
        # Configurar Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Intentar crear el driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except ImportError:
                raise Exception("No se pudo encontrar el driver de Chrome. Instala webdriver-manager: pip install webdriver-manager")
        
        wait = WebDriverWait(driver, 30)
        url_login = "https://login.satrack.com/login"
        
        # Login
        driver.get(url_login)
        usuario_input = wait.until(EC.presence_of_element_located((By.ID, "txt_login_username")))
        usuario_input.send_keys(username)
        contrasena_input = driver.find_element(By.ID, "txt_login_password")
        contrasena_input.send_keys(password)
        boton_login = driver.find_element(By.ID, "btn_login_login")
        boton_login.click()
        
        # Esperar a que carguen los vehículos
        try:
            wait_vehiculos = WebDriverWait(driver, 60)
            wait_vehiculos.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sidenav-location-container-menu")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".container-vehicle-list")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='container-vehicle-list']"))
                )
            )
        except Exception:
            pass  # Continuar aunque no se encuentre el contenedor
        
        # Buscar vehículos
        vehiculos_elements = driver.find_elements(By.CSS_SELECTOR, ".container-vehicle-list")
        if not vehiculos_elements:
            vehiculos_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='container-vehicle-list']")
        
        # Extraer datos de cada vehículo
        for i, vehiculo_element in enumerate(vehiculos_elements, 1):
            try:
                vehiculo_data = _extraer_datos_vehiculo(vehiculo_element, driver, i)
                if vehiculo_data:
                    vehiculos.append(vehiculo_data)
            except Exception as e:
                print(f"Error extrayendo vehículo {i}: {str(e)}")
                continue
        
        return vehiculos
        
    except Exception as e:
        raise Exception(f"Error durante el scraping: {str(e)}")
    finally:
        if driver:
            driver.quit()

def _extraer_datos_vehiculo(vehiculo_element, driver, index: int) -> Optional[Dict]:
    """
    Extrae los datos de un elemento de vehículo.
    
    Args:
        vehiculo_element: Elemento webdriver del vehículo
        driver: Instancia del webdriver
        index: Índice del vehículo
    
    Returns:
        Dict: Diccionario con los datos del vehículo o None si hay error
    """
    try:
        # Obtener ID del vehículo
        vehiculo_id = vehiculo_element.get_attribute("id")
        if not vehiculo_id:
            try:
                vehiculo_id = vehiculo_element.find_element(By.XPATH, ".//div[@id][1]").get_attribute("id")
            except:
                vehiculo_id = f"vehiculo_{index}"
        
        # Extraer placa
        placa = ""
        try:
            alias_element = vehiculo_element.find_element(By.CSS_SELECTOR, "[id$='_alias']")
            span_alias = alias_element.find_element(By.TAG_NAME, "span")
            placa = span_alias.text.strip()
        except:
            try:
                header = vehiculo_element.find_element(By.CSS_SELECTOR, ".row-header, .text-alarm-black")
                placa = header.text.strip()
            except:
                placa = vehiculo_id
        
        # Extraer dirección
        direccion = ""
        try:
            address_element = vehiculo_element.find_element(By.CSS_SELECTOR, "[id$='_address']")
            span_address = address_element.find_element(By.TAG_NAME, "span")
            direccion = span_address.text.strip()
        except:
            try:
                address_element = vehiculo_element.find_element(By.CSS_SELECTOR, ".address-text")
                direccion = address_element.text.strip()
            except:
                direccion = "No disponible"
        
        # Extraer coordenadas
        lat, lon = "", ""
        try:
            coords_text = vehiculo_element.get_attribute("data-coords")
            if coords_text and "," in coords_text:
                lat, lon = coords_text.split(",", 1)
            else:
                match = re.search(r"(-?\d+\.\d+),\s*(-?\d+\.\d+)", direccion)
                if match:
                    lat, lon = match.group(1), match.group(2)
        except:
            pass
        
        # Convertir coordenadas a float o usar 0.0 si no están disponibles
        try:
            latitud = float(lat.strip()) if lat else 0.0
            longitud = float(lon.strip()) if lon else 0.0
        except:
            latitud = 0.0
            longitud = 0.0
        
        # Extraer estado
        estado = ""
        try:
            icon_status = vehiculo_element.find_element(By.CSS_SELECTOR, ".icon-status")
            clases = icon_status.get_attribute("class")
            match = re.search(r'icon-(\w+)', clases)
            if match:
                estado = match.group(1)
            else:
                estado = "desconocido"
        except:
            estado = "no disponible"
        
        # Extraer fecha
        fecha = ""
        try:
            date_element = vehiculo_element.find_element(By.CSS_SELECTOR, "[id$='_date'], .last-report-time")
            fecha = date_element.text.strip()
        except:
            fecha = "No disponible"
        
        return {
            "placa": placa,
            "ubicacion": direccion,
            "latitud": latitud,
            "longitud": longitud,
            "estado": estado,
            "fecha_ultimo_reporte": fecha
        }
        
    except Exception as e:
        print(f"Error extrayendo datos del vehículo: {str(e)}")
        return None

def scrape_vehiculos_satrack_y_guardar(username: str, password: str, callback_guardar: Callable, 
                                      datos_adicionales: Dict = None, headless: bool = False,
                                      sobrescribir: bool = False) -> Dict:
    """
    Extrae información de vehículos desde Satrack y los guarda directamente en la base de datos.
    
    Args:
        username: Usuario de Satrack
        password: Contraseña de Satrack
        callback_guardar: Función callback que recibe los datos del vehículo y los guarda en BD
                         Debe recibir: (vehiculo_data: Dict, datos_adicionales: Dict) -> Dict
                         Debe retornar: {"guardado": bool, "actualizado": bool, "error": str}
        datos_adicionales: Diccionario con datos adicionales del Excel (marca, modelo, etc.)
        headless: Si True, ejecuta el navegador en modo headless
    
    Returns:
        Dict: Estadísticas del proceso
        {
            "exitoso": bool,
            "total_encontrados": int,
            "guardados": int,
            "actualizados": int,
            "errores": int,
            "errores_detalle": List[str]
        }
    """
    driver = None
    estadisticas = {
        "exitoso": False,
        "total_encontrados": 0,
        "guardados": 0,
        "actualizados": 0,
        "errores": 0,
        "errores_detalle": []
    }
    
    try:
        # Configurar Chrome
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Intentar crear el driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except ImportError:
                raise Exception("No se pudo encontrar el driver de Chrome. Instala webdriver-manager: pip install webdriver-manager")
        
        wait = WebDriverWait(driver, 30)
        url_login = "https://login.satrack.com/login"
        
        # Login
        driver.get(url_login)
        usuario_input = wait.until(EC.presence_of_element_located((By.ID, "txt_login_username")))
        usuario_input.send_keys(username)
        contrasena_input = driver.find_element(By.ID, "txt_login_password")
        contrasena_input.send_keys(password)
        boton_login = driver.find_element(By.ID, "btn_login_login")
        boton_login.click()
        
        # Esperar a que carguen los vehículos
        try:
            wait_vehiculos = WebDriverWait(driver, 60)
            wait_vehiculos.until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sidenav-location-container-menu")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".container-vehicle-list")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='container-vehicle-list']"))
                )
            )
        except Exception:
            pass  # Continuar aunque no se encuentre el contenedor
        
        # Buscar vehículos
        vehiculos_elements = driver.find_elements(By.CSS_SELECTOR, ".container-vehicle-list")
        if not vehiculos_elements:
            vehiculos_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='container-vehicle-list']")
        
        # Extraer y guardar datos de cada vehículo inmediatamente
        for i, vehiculo_element in enumerate(vehiculos_elements, 1):
            try:
                vehiculo_data = _extraer_datos_vehiculo(vehiculo_element, driver, i)
                if vehiculo_data:
                    estadisticas["total_encontrados"] += 1
                    
                    # Guardar directamente en la base de datos
                    resultado_guardado = callback_guardar(vehiculo_data, datos_adicionales or {}, sobrescribir)
                    
                    if resultado_guardado.get("guardado"):
                        estadisticas["guardados"] += 1
                    elif resultado_guardado.get("actualizado"):
                        estadisticas["actualizados"] += 1
                    else:
                        estadisticas["errores"] += 1
                        error_msg = resultado_guardado.get("error", "Error desconocido")
                        estadisticas["errores_detalle"].append(f"Vehículo {vehiculo_data.get('placa', 'desconocido')}: {error_msg}")
                        
            except Exception as e:
                estadisticas["errores"] += 1
                estadisticas["errores_detalle"].append(f"Error extrayendo vehículo {i}: {str(e)}")
                continue
        
        estadisticas["exitoso"] = True
        return estadisticas
        
    except Exception as e:
        estadisticas["errores_detalle"].append(f"Error durante el scraping: {str(e)}")
        return estadisticas
    finally:
        if driver:
            driver.quit()

def process_coordinates(coordinates_str: str) -> tuple:
    """
    Procesa el string de coordenadas y retorna latitud y longitud.
    
    Args:
        coordinates_str: String con coordenadas en formato "lat,lon"
    
    Returns:
        tuple: (latitud, longitud) como strings, o ('', '') si hay error
    """
    try:
        if not coordinates_str or coordinates_str == 'No disponible':
            return '', ''
        coords_clean = coordinates_str.replace(' ', '').strip()
        if ',' in coords_clean:
            lat, lon = coords_clean.split(',', 1)
        elif ';' in coords_clean:
            lat, lon = coords_clean.split(';', 1)
        else:
            return '', ''
        try:
            float(lat)
            float(lon)
            return lat.strip(), lon.strip()
        except ValueError:
            return '', ''
    except Exception:
        return '', ''