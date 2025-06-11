import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def scrape_comisiones():
    # URL de la página
    url = "https://www.hcdn.gov.ar/comisiones/agenda/"
    
    try:
        print("Accediendo a la URL:", url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print("Procesando contenido...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lista para almacenar todas las reuniones
        reuniones = []
        fecha_actual = None
        
        # Encontrar la tabla principal
        tabla = soup.find('table')
        if not tabla:
            print("⚠️ No se encontró ninguna tabla en la página")
            return None
            
        # Encontrar todas las filas de la tabla
        rows = tabla.find_all('tr')
        print(f"Se encontraron {len(rows)} filas en la tabla")
        
        # Debug: Mostrar el HTML de las filas que podrían contener fechas
        print("\nExaminando filas para fechas:")
        for row in rows:
            if len(row.find_all('td')) != 2:  # Si no tiene dos celdas, podría ser una fecha
                print("\nPosible fila de fecha:")
                print(row.prettify())
        
        # Procesar las filas
        for row in rows:
            # Primero intentamos encontrar si es una fila de fecha (th)
            th = row.find('th')
            if th and th.get('colspan') == '2':
                texto_fecha = th.get_text(strip=True)
                if any(dia in texto_fecha.lower() for dia in ['lunes', 'martes', 'miércoles', 'jueves', 'viernes']):
                    fecha_actual = texto_fecha
                    print(f"\n📅 Nueva fecha encontrada: {fecha_actual}")
                    continue
            
            # Si no es fecha, procesamos como reunión si tiene dos celdas
            cells = row.find_all('td')
            if len(cells) == 2:
                texto_celda1 = cells[0].get_text(strip=True)
                texto_celda2 = cells[1].get_text(strip=True)
                
                # Extraer hora y sala de la primera celda
                hora_match = re.match(r'(\d{1,2}:\d{2})(.*)', texto_celda1)
                if hora_match:
                    hora = hora_match.group(1)
                    sala = hora_match.group(2).strip()
                    
                    # Extraer comisión y descripción de la segunda celda
                    partes = texto_celda2.split('.')
                    comision = partes[0].strip()
                    descripcion = '.'.join(partes[1:]).strip() if len(partes) > 1 else ''
                    
                    # Buscar el enlace de la citación
                    citacion_link = cells[1].find('a', href=True)
                    citacion_url = citacion_link['href'] if citacion_link else ""
                    
                    reunion = {
                        'fecha': fecha_actual,
                        'hora': hora,
                        'sala': sala,
                        'comision': comision,
                        'descripcion': descripcion,
                        'citacion_url': citacion_url
                    }
                    
                    reuniones.append(reunion)
                    print(f"\n✓ Nueva reunión encontrada:")
                    print(f"  Fecha: {fecha_actual}")
                    print(f"  Hora: {hora}")
                    print(f"  Sala: {sala}")
                    print(f"  Comisión: {comision}")
                    print(f"  Descripción: {descripcion[:100]}...")
        
        print(f"\nTotal de reuniones encontradas: {len(reuniones)}")
        
        if not reuniones:
            print("⚠️ No se encontraron reuniones")
            return None
        
        # Crear DataFrame
        df = pd.DataFrame(reuniones)
        
        # Guardar en CSV
        filename = f'agenda_comisiones_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✅ Datos guardados exitosamente en {filename}")
        
        # Mostrar las primeras filas del DataFrame
        print("\nPrimeras entradas del DataFrame:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("🔄 Iniciando scraping de la agenda de comisiones...")
    df = scrape_comisiones()
    if df is not None:
        print("\n📊 Resumen final:")
        print(f"Total de reuniones en el DataFrame: {len(df)}")
        print("\nColumnas del DataFrame:")
        print(df.columns.tolist()) 