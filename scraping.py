import requests #para hacer peticiones http
from bs4 import BeautifulSoup #para parsear html
import pandas as pd # para analizar y manejar datitos, 
import re # sirve para buscar, validar y limpiar textos, para expresiones regulares, es rapido
from datetime import datetime #fechas
from urllib.parse import urljoin # unir urls relativas con absolutas

#palabras claves 
palabras_claves = re.compile(
    r'\sparo?s\s|paran|asamblea|huelga|marcha|cortes? de ruta|cortan ruta|corte? de calle|cortan calle|'
    r'trabaj[a-zA-Z]*|sindica[a-zA-Z]*|paritari[a-zA-Z]*|gremi[a-zA-Z]*|cgt|'
    r'\suta\s|\sate\s|luz y fuerza|uepc|\ssep\s|\sutep\s|surrbac|economia popular|economia informal|'
    r'conflicto|despid[a-zA-Z]*|salar[a-zA-Z]*|transporte|aguinaldo|sueldo|bancaria|'
    r'delegad[a-zA-Z]*|limpieza|precariza[a-zA-Z]*|cadete|repartidor[a-zA-Z]*|aplicaciones|'
    r'suspen[a-zA-Z]*|laboral[a-zA-Z]*|conciliacion|moviliz[a-zA-Z]*|ajuste|protest[a-zA-Z]*|derechos?|cortes?',
    flags=re.IGNORECASE
)

''' funciones auxiliares '''
#conseguir los enlaces, consta de 2 parametros: la url y la tematica o etiqueta
def get_scraping_links(page_url, tag_link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/140.0.0.0 Safari/537.36"
    }
    r = requests.get(page_url, headers=headers) #obtiene el url
    soup = BeautifulSoup(r.text, 'html.parser') #parsea el html
    links = [urljoin(page_url, a.get("href")) for a in soup.select(tag_link)] #fijarse luego
    return links

''' esta funcion extrae la seccion del link, ejemplo: 
extract section("https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123")
Devuelve: "provincia-de-buenos-aires" 
'''
#IMPORTANTE: aplicar un flitro de cordoba, solo de cordoba con izquierda diario, los demas diarios son locales
def extraer_seccion(url): #preguntar luego si es correcto
    url = url.lower()
    match = re.search(r'\.com/([^/]+)/', url) #busca el patron .com/ seguido de cualquier caracter que no sea /, una o mas veces, seguido de /
    print(match)
    print(match.group(1) if match else "NA")
    return match.group(1) if match else "NA" #si encuentra el patron devuelve el primer elemento del grupo, sino NA

"""esta funcion devuelve la cantidad de palabras en el link,
ejemplo: link_length("https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123")
devuelve: 1 donde 1 es la cantidad de palabras en la seccion del link que es noticia123"
"""
#TENER CUIDAdo con esto
#fijarse bien luego, este siempre devuelve el ultimo elemento del link
def link_length(url):  #fijarse bien luego, este siempre devuelve el ultimo elemento del link
    url = re.sub(r'https://.*/', '', url.strip("/")) #elimina el diario y la barra al final
    print("Holiiiiiiiiiiiiiiiiis")
    print(url.split("-"))
    return len(url.split("-")) ##no se si deberia 1 


def create_tag(url):
    url = url.lower() #convierte a minusculas
    url = re.sub(r'https://.*/', '', url.strip("/")) #elimina el diario y la barra al final
    print("URL EN CREATE TAG")
    print(url)
    url = (url.replace("á","a").replace("é","e")
              .replace("í","i").replace("ó","o").replace("ú","u")
              .replace("-", " ")) #elimina tildes y reemplaza guiones por espacios
    tags = palabras_claves.findall(url) #busca todas las coincidencias de palabras claves en el url
    return " ".join(tags)


# ejemplo de uso create tag
"""
texto = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés/noticia123"
print(create_tag(texto))
"""
"""""
# URL que queremos analizar
pagina = "https://www.laizquierdadiario.com/"

# Selector de etiquetas: todas las etiquetas <a>
selector = "a"

# Llamamos a la función
enlaces = get_scraping_links(pagina, selector)

# Mostramos los primeros 10 enlaces
print(enlaces[:10])


textos= [
    "El gremio discute paritarias con el gobierno.",
    "Se realizó una asamblea de trabajadores.",
    "Los sindicalistas organizaron una huelga.",
    "el bajo salario de lxs docentes",
    "uta esta en paro",
    "la economia popular esta en auge, ojala no haya ajuste, muy utopico en la Argentina a la que gobierna Milei",
    "pinpon es un munieco muy guapo y de carton",
    "BASTA DE RECORTE SALARIAL!"
]

for t in textos:
    if palabras_claves.search(t):
        print("Coincidencia:", t)
        """
# funcion para obtener los links, se usa en crate_links
# def get_scraping_links():

# para linux fedora instalar:
# /bin/python -m pip install --user pandas
# para windows
#  Pulsa Win + R, escribe cmd y presiona Enter o
#Busca PowerShell y ábrelo.
# python -m pip install --user pandas
# o, si tienes el lanzador de Python (py):
# py -m pip install --user pandas


# para bautiful soup instalar:   pip install requests beautifulsoup4


