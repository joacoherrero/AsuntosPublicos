import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def scrape_senado():
    # URL de la página
    url = "https://www.senado.gob.ar/parlamentario/comisiones/?active=permanente"
    
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
        
        # Encontrar la tabla de agenda de reuniones
        # La tabla está después del encabezado "Agenda de Reuniones"
        agenda_header = soup.find('h1', string='Agenda de Reuniones')
        if not agenda_header:
            print("⚠️ No se encontró la sección de agenda")
            return None
            
        # Buscar la tabla después del encabezado
        tabla = agenda_header.find_next('table')
        if not tabla:
            print("⚠️ No se encontró la tabla de reuniones")
            return None
        
        # Procesar las filas de la tabla
        rows = tabla.find_all('tr')
        print(f"Se encontraron {len(rows)} filas en la tabla")
        
        for row in rows:
            # Obtener todas las celdas de la fila
            cells = row.find_all('td')
            
            if len(cells) == 3:  # La tabla tiene 3 columnas: Comisión, Día y Hora, Próxima Reunión
                comision = cells[0].get_text(strip=True)
                dia_hora = cells[1].get_text(strip=True)
                agenda_link = cells[2].find('a')['href'] if cells[2].find('a') else ""
                
                # Procesar día y hora
                # El formato suele ser "ASESORES - Día de la semana DD de mes - HH:mm h"
                dia_hora_parts = dia_hora.split('-')
                tipo_reunion = dia_hora_parts[0].strip() if len(dia_hora_parts) > 1 else ""
                
                # Extraer fecha y hora usando expresiones regulares
                fecha_match = re.search(r'(\w+\s+\d+\s+de\s+\w+)', dia_hora)
                hora_match = re.search(r'(\d{1,2}:\d{2})\s*h', dia_hora)
                
                fecha = fecha_match.group(1) if fecha_match else ""
                hora = hora_match.group(1) if hora_match else ""
                
                reunion = {
                    'comision': comision,
                    'tipo_reunion': tipo_reunion,
                    'fecha': fecha,
                    'hora': hora,
                    'dia_hora_completo': dia_hora,
                    'agenda_url': f"https://www.senado.gob.ar{agenda_link}" if agenda_link else ""
                }
                
                reuniones.append(reunion)
                print(f"\n✓ Nueva reunión encontrada:")
                print(f"  Comisión: {comision}")
                print(f"  Tipo: {tipo_reunion}")
                print(f"  Fecha: {fecha}")
                print(f"  Hora: {hora}")
        
        print(f"\nTotal de reuniones encontradas: {len(reuniones)}")
        
        if not reuniones:
            print("⚠️ No se encontraron reuniones")
            return None
        
        # Crear DataFrame
        df = pd.DataFrame(reuniones)
        
        # Guardar en CSV
        filename = f'agenda_senado_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
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
    print("🔄 Iniciando scraping de comisiones del Senado...")
    df = scrape_senado()
    if df is not None:
        print("\n📊 Resumen final:")
        print(f"Total de reuniones en el DataFrame: {len(df)}")
        print("\nColumnas del DataFrame:")
        print(df.columns.tolist()) 