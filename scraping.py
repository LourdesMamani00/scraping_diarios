import requests #para hacer peticiones http
from bs4 import BeautifulSoup #para parsear html
import pandas as pd # para analizar y manejar datitos, 
import re # sirve para buscar, validar y limpiar textos, para expresiones regulares, es rapido
from datetime import date, datetime #fechas
from urllib.parse import urljoin # unir urls relativas con absolutas
import os #para manejar archivos y directorios
from newspaper import Article, Config # newspaper es para hacer scrapping de diarios
import locale #para saber el mes en español
import unicodedata #para manejar caracteres especiales



#########################################################################################################
#   CONFIGURACIONES INICIALES
########################################################################################################

########################################
# 1. PALABRAS CLAVES
########################################

PALABRAS_CLAVES = re.compile(
    r'\bparo[a-zA-Z]*\b|\bparan\b|\basamblea[s]?\b|\bhuelga\b|\bmarcha\b|'
    r'\bcortes? de ruta\b|\bcortan ruta\b|\bcortes? de calle\b|\bcortan calle\b|'
    r'\btrabaj[a-zA-Z]*\b|\bsindica[a-zA-Z]*\b|\bparitari[a-zA-Z]*\b|\bgremi[a-zA-Z]*\b|'
    r'\bcgt\b|\buta\b|\bate\b|\bluz y fuerza\b|\buepc\b|\bsep\b|\butep\b|\bsurrbac\b|'
    r'\beconomia popular\b|\beconomia informal\b|\bconflicto\b|\bdespid[a-zA-Z]*\b|'
    r'\bsalar[a-zA-Z]*\b|\btransporte\b|\baguinaldo\b|\bsueldo\b|\bbancaria\b|'
    r'\bdelegad[a-zA-Z]*\b|\blimpieza\b|\bprecariza[a-zA-Z]*\b|\bcadete\b|'
    r'\brepartidor[a-zA-Z]*\b|\baplicaciones\b|\bsuspen[a-zA-Z]*\b|\blaboral[a-zA-Z]*\b|'
    r'\bconciliacion\b|\bmoviliz[a-zA-Z]*\b|\bajuste\b|\bprotest[a-zA-Z]*\b|\bderechos?\b|\bcortes?\b',
    flags=re.IGNORECASE
)

#----------------------------------------------------------------------
#########################################
# 2. DIARIOS, CARPETAS Y ETIQUETAS (PARAMETROS DE LOS DIARIOS)
#########################################

DIARIOS = [
    "https://www.laizquierdadiario.com/",
    "https://www.lavoz.com.ar/",
    "http://www.lavozdesanjusto.com.ar/",
    "https://www.eldiariocba.com.ar/",
    "https://www.cba24n.com.ar/",
    "https://www.puntal.com.ar/",
]

NOMBRE_DEL_DIARIO = [
    "la_izquierda",
    "la_voz_del_interior",
    "la_voz_de_san_justo",
    "el_diario_villa_maria",
    "cba24n",
    "puntal_rio_cuarto",
]

''' Los html tags son las reglas o patrones de busqueda que se usan para beautifullsoup. Ejemplo:
<div class="columnista">
  <a href="nota1.html">Nota 1</a>
</div>
<h2><a href="nota2.html">Nota 2</a></h2>
----------------------------------------------
soup.select("div.columnista a")
lo que encontro: <a href="nota1.html">Nota 1</a>
'''
HTML_TAGS = [
    ["div.columnista a", "h2 a", "h3 a"],
    ["h2 a", "h1 a", "article a", "main article seccion h1", "div article a", "article a"],
    ["a"], 
    ["h2 a"],
    ["div a"],
    ["h1 a", "h2 a", "h3 a", "article a", "figure a"],
]

####################################################################################################################
# FUNCIONES AUXILIARES
##################################################################################################################

#conseguir los enlaces, consta de 2 parametros: la url y la tematica o etiqueta
def get_scraping_links(pag_web, tag_link):
    """Obtiene todos los enlaces válidos desde una página HTML."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(pag_web, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[WARN] No se pudo acceder a {pag_web} - Código {resp.status_code}")
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = []
        for tag in soup.select(tag_link):
            href = tag.get("href")
            if href:
                full_link = requests.compat.urljoin(pag_web, href)
                links.append(full_link)
        return list(set(links))
    except Exception as e:
        print(f"[ERROR] scraping_links({pag_web}): {e}")
        return []


#IMPORTANTE: aplicar un flitro de cordoba, solo de cordoba con izquierda diario, los demas diarios son locales
def extraer_seccion(url): 
    ''' esta funcion extrae la seccion del link, ejemplo: extract section("https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123")
    Devuelve: "provincia-de-buenos-aires" . Si no encuentra la seccion devuelve "NA"'''
    url = url.lower()
    match = re.search(r'\.com(?:\.ar)?/([^/]+)/?', url) #busca el patron .com/ seguido de cualquier caracter que no sea /, una o mas veces, seguido de /
    return match.group(1) if match else "NA" #si encuentra el patron devuelve el primer elemento del grupo, sino NA
#print("extraer seccion:")
#link = "https://www.lavoz.com.ar/ciudadanos/centros-de-jubilados-denuncian-demoras-en-pagos-de-pami-por-los-talleres-sociopreventivos/"
#extraer_seccion(link)
#print("FIN DE EXTRAER SECCION")


def link_length(url):  #fijarse bien luego, este siempre devuelve el ultimo elemento del link
    """esta funcion devuelve la cantidad de palabras en el link, ejemplo: link_length("https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123-extra-paro")
    devuelve: 3 donde  es la cantidad de palabras en la seccion del link que es noticia123 extra paro"
    """
    url = re.sub(r'https://.*/', '', url.strip("/")) #elimina el diario y la barra al final
    return len(url.split("-")) #divide el link en palabras separadas por guiones y devuelve la cantidad de palabras

# print("FIN DE LINK LENGTH")
# link = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123-extra-paro"
# print(link_length(link))
# print("FIN DE LINK LENGTH")

def create_tags(url):
    """esta funcion crea tags a partir del link, ejemplo:
    create_tag("https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés/casas-paro-noticia123")
    devuelve: "paro"
    """
    url = url.lower() #convierte a minusculas
    url = re.sub(r'https://.*/', '', url.strip("/")) #elimina el diario y la barra al final
    url = (url.replace("á","a").replace("é","e")
              .replace("í","i").replace("ó","o").replace("ú","u")
              .replace("-", " ")) #elimina tildes y reemplaza guiones por espacios
    tags = PALABRAS_CLAVES.findall(url) #busca todas las coincidencias de palabras claves en el url
    return " ".join(tags) #une las palabras claves encontradas en una sola cadena separada por espacios, si no encuentra palabras claves devuelve vacio ' '


# ejemplo de uso create tag, CREO QUE ESTA MAL, FIJARSE QUE ONDA CON LAS EXPRESIONES REGULARES
#ejemplo = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés-paro-trabajadores/paro-noticia123/"
"""
ejemplo= "https://www.lavoz.com.ar/ciudadanos/cortes-de-calle-utep-transporte-urbano-de-cordoba-podria-haber-asambleas-la-semana-proxima/"
print("EJEMPLO DE CREATE TAG")
print("este es el ejemplo: ")
print(create_tags(ejemplo))

print("FIN DEL EJEMPLO DE CREATE TAG")
url = "https://www.laizquierdadiario.com/huelga-Trabajadores-en-huelga-por-mejores-salarios-paro"
print(create_tags(url))
"""
#----------------------------------------------------------------------

def crear_enlaces(diario, html_tags):
    """ Crea un Dataframe  con las fechas, los diarios, los links, la seccion, el tamanio del link y las palabras claves """
    links = []
    for tag in html_tags:
        links.extend(get_scraping_links(diario, tag))
    links = list(set(links))  # Elimina duplicados
    print(f"[INFO] {len(links)} enlaces encontrados en {diario}")
    
    if "laizquierdadiario.com" in diario:
        provincia = "Cordoba"
        filtro_url = f"laizquierdadiario.com/{provincia}"
        links_filtrados = [link for link in links if filtro_url in link]

        print(f"[INFO] {len(links_filtrados)} enlaces encontrados de {provincia} en {diario}")

        links = links_filtrados
    
    data = []
    for link in links:
        data.append({
            "fecha": date.today().strftime("%d-%m-%Y"),
            "diario": diario,
            "link": link,
            "seccion": extraer_seccion(link), #devuelve la seccion del link o NA
            #"tamanio_link": link_length(link), #devuelve la cantidad de palabras que vienen luego de la seccion
            "palabras_claves": create_tags(link) #devuelve la palabra clave encontrada en el link, fijarse que onda con la palabra claave paro
        })
    df = pd.DataFrame(data)
    return df

#diario = "https://www.laizquierdadiario.com/"
#html_tags = ["div.columnista a", "h2 a", "h3 a"]

#diario = "https://www.lavoz.com.ar/"
#html_tags = ["h2 a", "h1 a, article a", "main article seccion h1", "div article a", "article a"]

#en la voz de san justo no tienen "seccion como tal, tiene otra forma de definir los links por "seccion""
# diario = "https://www.lavozdesanjusto.com.ar/"
# html_tags = ["a", "main seccion div article a", "article a"]

# diario = "https://www.eldiariocba.com.ar/"
# html_tags = ["h2 a"] #div article div a

# diario = "https://www.cba24n.com.ar/"
# html_tags = ["div a"]

# diario =     "https://www.puntal.com.ar/"
# html_tags = ["h1 a", "h2 a", "h3 a", "figure a"] #div article figure a

#df = crear_enlaces(diario, html_tags)
# # Mostrar solo las filas donde 'palabras_claves' no está vacía
#df_filtrado = df[df["palabras_claves"].notna() & (df["palabras_claves"] != "")]
#print(df_filtrado)

#print(df.head(60))

#print(df.head())

def obtener_titulo_y_contenido(url, diario=None):
    """Obtiene el título y el contenido de una noticia dada su URL y las etiquetas HTML correspondientes."""
    try:
        if "puntal.com.ar" in diario:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"[WARN] No se pudo acceder a {url} - Código {resp.status_code}")
                return None, None
            soup = BeautifulSoup(resp.text, 'html.parser')

            for footer in soup.find_all('footer'):
                footer.decompose()  # lo borra del árbol HTML el footer
            #Buscar todos los párrafos dentro de cualquier <article>
            contenido_tags = soup.select('article p')
            #titulo
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else None
            #contenido
            content = '\n'.join(p.get_text(strip=True) for p in contenido_tags) if contenido_tags else None
            return title, content
        else:
            articulo = Article(url)
            articulo.download()
            articulo.parse()
            return articulo.title, articulo.text
    except Exception as e:
        print(f"[ERROR] obtener_titulo_y_contenido({url}): {e}")
        return None, None   
        
#la voz del interior
# url = "https://www.lavoz.com.ar/servicios/bono-de-100000-para-jubilados-cordobeses-cuando-se-paga-y-a-quienes-les-corresponde/"
# titulo, contenido = obtener_titulo_y_contenido(url)
# print("Titulo:", titulo)
# print("Contenido:", contenido[:500])  # Muestra solo los primeros 500 caracteres del contenido

# #el puntal
# url = "https://www.puntal.com.ar/marc-marquez/marc-marquez-tuvo-que-ser-operado-nuevamente-del-hombro-derecho-y-se-pierde-el-resto-del-campeonato-n244656"
# diario = "https://www.puntal.com.ar/"
# titulo, contenido = obtener_titulo_y_contenido(url, diario)
# print("Titulo:", titulo)
# print("Contenido:", contenido[:500])  # Muestra solo los primeros 500 caracteres del contenido

def limpiar_texto_completo(texto):
    if not texto:
        return ""
    
    texto = unicodedata.normalize('NFKC', texto)
    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    texto = texto.replace('\u00A0', ' ')
    texto = re.sub(r'[\u200B-\u200F\uFEFF]', '', texto)
    texto = ''.join(ch for ch in texto if unicodedata.category(ch)[0] not in ('C',))
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

##################################################################################################################
#   FUNCION PRINCIPAL — SCRAPING MENSUAL CONSOLIDADO
##################################################################################################################

# Lista donde vamos a acumular los dataframes de todos los diarios 
df_consolidado = []

for i, diario in enumerate(DIARIOS):
    print(f"\n[INFO] Procesando {diario}...")
    df_sin_filtro = crear_enlaces(diario, HTML_TAGS[i])
    if df_sin_filtro.empty:
        print(f"[WARN] No se encontraron enlaces en {diario}")
        continue

    # Filtrar solo links con palabras clave
    df = df_sin_filtro[df_sin_filtro["palabras_claves"].notna() & (df_sin_filtro["palabras_claves"] != "")]

    # Excluir secciones según diario
    if "lavoz.com.ar" in diario:
        excluir = ['avisos', 'vos', 'NA', 'deportes', 'espacio-de-marca', 'espacio-publicidad', 'tendencias']
    elif "lavozdesanjusto.com.ar" in diario:
        excluir = ['NA', 'suplementos']
    elif "eldiariocba.com.ar" in diario:
        excluir = ['culturales', 'el-equipo', 'espacio-patrocinado']
    elif "cba24n.com.ar" in diario:
        excluir = ['deportes', 'tecnologia', 'espectaculos', 'programa', 'contenido-de-marca', 'vamos-al-movil']
    else:
        excluir = []

    df = df[~df['seccion'].isin(excluir)]

    # Agregar columnas de título y contenido
    df["titulo"] = None
    df["contenido"] = None
    df["palabras_claves"] = df["palabras_claves"].apply(limpiar_texto_completo)

    for idx, row in df.iterrows():
        titulo, contenido = obtener_titulo_y_contenido(row["link"], diario)
        # Limpiar antes de asignar
        df.at[idx, "titulo"] = limpiar_texto_completo(titulo)
        df.at[idx, "contenido"] = limpiar_texto_completo(contenido)
    #asegura que no tenga valores nulos sino cadenas vacias, ni salto de lineas
    #df["contenido"] = df["contenido"].fillna("").str.replace("\n", " ", regex=False)
    # Asegurar que no haya NaN
    df["titulo"] = df["titulo"].fillna("")
    df["contenido"] = df["contenido"].fillna("")
    # Guardamos la info del diario actual en el consolidado general
    df_consolidado.append(df)
    print(f"[OK] Procesado {len(df)} enlaces de {NOMBRE_DEL_DIARIO[i]}")

# ------------------------------------------------------------------
#  GUARDADO  MENSUAL EN EXCEL CONSOLIDADO
# ------------------------------------------------------------------

if df_consolidado:
    df_final = pd.concat(df_consolidado, ignore_index=True).drop_duplicates(subset=["link"])

    # Mes y año actual
    #mes_actual = datetime.now().strftime("%B_%Y").lower()  # ejemplo: "octubre_2025"
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    mes_actual = datetime.now().strftime("%B_%Y").lower()

    # Crear carpeta de salida (una sola general)
    carpeta_salida = "noticias_mensuales"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Archivo mensual consolidado
    filepath = os.path.join(carpeta_salida, f"{mes_actual}_noticias.xlsx")

    # Si ya existe, lo cargamos para agregar nuevas noticias
    if os.path.exists(filepath):
        df_existente = pd.read_excel(filepath)
        df_final = pd.concat([df_existente, df_final]).drop_duplicates(subset=["link"])

    df_final = df_final.drop(columns=["seccion"], errors="ignore")

    df_final.to_excel(filepath, index=False)
    print(f"\n Archivo mensual consolidado actualizado: {filepath}")
    print(f"   Total de noticias: {len(df_final)}")
else:
    print("\n[INFO] No se encontraron noticias con palabras clave en ningún diario.")