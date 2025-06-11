# Importación de bibliotecas necesarias
# feedparser: Para procesar y leer feeds RSS
# datetime: Para manejar fechas y horas
# dateutil.parser: Para analizar fechas en diferentes formatos
import feedparser
from datetime import datetime, timedelta
from dateutil import parser
import time
import pandas as pd

class RSSReader:
    def __init__(self):
        # Inicializa un diccionario vacío para almacenar los feeds RSS
        # Cada feed se guardará con un nombre como clave y su URL como valor
        self.feeds = {}
        # Configurar feedparser para manejar errores de codificación
        feedparser.PREFERRED_XML_PARSERS = ["html.parser"]
    
    def add_feed(self, name, url):
        """Añade un nuevo feed RSS a la lista de feeds a monitorear."""
        # Almacena un nuevo feed en el diccionario usando el nombre como clave y la URL como valor
        self.feeds[name] = url
    
    def _is_recent_entry(self, published_date_str, max_days_old=7):
        """Verifica si una entrada es del día actual."""
        if not published_date_str:
            return False
            
        try:
            # Parsear la fecha de publicación
            published_date = parser.parse(published_date_str)
            # Obtener la fecha actual
            current_date = datetime.now()
            # Verificar si la fecha de publicación es del día actual
            return (
                published_date.year == current_date.year and
                published_date.month == current_date.month and
                published_date.day == current_date.day
            )
        except Exception as e:
            print(f"⚠️ Error al parsear fecha de publicación: {str(e)}")
            return False

    def get_feed_entries(self, feed_name, limit=10):
        """Obtiene las últimas entradas de un feed específico."""
        # Verifica si el feed solicitado existe en nuestro diccionario
        if feed_name not in self.feeds:
            raise ValueError(f"Feed '{feed_name}' no encontrado")
        
        # Utiliza feedparser para obtener y analizar el contenido del feed RSS
        try:
            feed = feedparser.parse(self.feeds[feed_name])
            
            if hasattr(feed, 'status') and feed.status != 200:
                print(f"⚠️ Advertencia: El feed {feed_name} retornó estado {feed.status}")
            
            if not feed.entries:
                print(f"⚠️ Advertencia: No se encontraron entradas en el feed {feed_name}")
                return []
            
            entries = []
            # Procesa cada entrada del feed hasta el límite especificado
            for entry in feed.entries:
                try:
                    published = None
                    if hasattr(entry, 'published'):
                        published = entry.published
                    elif hasattr(entry, 'updated'):
                        published = entry.updated
                        
                    # Verificar si la entrada es reciente
                    if not self._is_recent_entry(published):
                        continue
                    
                    entry_data = {
                        'title': entry.title if hasattr(entry, 'title') else 'Sin título',
                        'link': entry.link if hasattr(entry, 'link') else None,
                        'published': published,
                        'summary': entry.summary if hasattr(entry, 'summary') else None,
                        'feed_name': feed_name
                    }
                    entries.append(entry_data)
                    
                    # Si ya tenemos suficientes entradas recientes, salimos
                    if len(entries) >= limit:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error al procesar entrada de {feed_name}: {str(e)}")
                    continue
            
            return entries
            
        except Exception as e:
            print(f"❌ Error al obtener el feed {feed_name}: {str(e)}")
            return []
    
    def get_latest_entries(self, feed_name, limit=10):
        """Obtiene las últimas entradas de un feed específico."""
        return self.get_feed_entries(feed_name, limit)
    
    def get_all_latest_entries(self, limit=10):
        """Obtiene las últimas entradas de todos los feeds registrados."""
        # Crea un diccionario para almacenar las entradas de todos los feeds
        all_entries = {}
        # Itera sobre cada feed registrado y obtiene sus últimas entradas
        for feed_name in self.feeds:
            try:
                entries = self.get_feed_entries(feed_name, limit)
                if entries:
                    all_entries[feed_name] = entries
            except Exception as e:
                print(f"Error al obtener entradas de {feed_name}: {str(e)}")
        return all_entries 

def parse_rss_feed(url, categoria):
    """
    Parsea un feed RSS y retorna una lista de noticias
    """
    try:
        feed = feedparser.parse(url)
        noticias = []
        
        print(f"\nProcesando feed de {categoria}...")
        for entry in feed.entries:
            noticia = {
                'categoria': categoria,
                'titulo': entry.title,
                'descripcion': entry.description if 'description' in entry else '',
                'link': entry.link,
                'fecha': entry.published if 'published' in entry else '',
            }
            noticias.append(noticia)
            print(f"Noticia agregada: {noticia['titulo']}")
            
        return noticias
    except Exception as e:
        print(f"Error al procesar el feed {categoria}: {str(e)}")
        return []

def main():
    # Definir los feeds
    feeds = [
        {
            'url': 'http://www.lapoliticaonline.com.ar/files/rss/ultimasnoticias.xml',
            'categoria': 'Últimas noticias'
        },
        {
            'url': 'http://www.lapoliticaonline.com.ar/files/rss/politica.xml',
            'categoria': 'Política'
        },
        {
            'url': 'http://www.lapoliticaonline.com.ar/files/rss/economia.xml',
            'categoria': 'Economía'
        }
    ]
    
    # Lista para almacenar todas las noticias
    todas_las_noticias = []
    
    print("Iniciando lectura de feeds RSS...")
    
    # Procesar cada feed
    for feed in feeds:
        noticias = parse_rss_feed(feed['url'], feed['categoria'])
        todas_las_noticias.extend(noticias)
    
    # Crear DataFrame
    if todas_las_noticias:
        df = pd.DataFrame(todas_las_noticias)
        
        # Guardar en CSV
        filename = f'noticias_lpo_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nSe guardaron {len(todas_las_noticias)} noticias en {filename}")
        
        # Mostrar resumen
        print("\nResumen por categoría:")
        print(df['categoria'].value_counts())
    else:
        print("\nNo se encontraron noticias para procesar.")

if __name__ == "__main__":
    main() 