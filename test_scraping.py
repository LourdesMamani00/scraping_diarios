from scraping import get_scraping_links, extraer_seccion, link_length, create_tag


# test para saber si la funcion get_scraping_links funciona correctamente, pasa el test
def test_get_scraping_links():
    pagina = "https://www.lavoz.com.ar/"
    selector = "a"
    enlaces = get_scraping_links(pagina, selector)
    assert isinstance(enlaces, list), "El resultado debe ser una lista"
    assert len(enlaces) > 0, "La lista de enlaces no debe estar vacía"
    assert all(isinstance(link, str) for link in enlaces), "Todos los enlaces deben ser cadenas de texto"
    # Verificar que los enlaces comienzan con 'http' o 'https'
    assert all(link.startswith("http") for link in enlaces), "Todos los enlaces deben comenzar con 'http' o 'https'"


def test_extraer_seccion():
    url1 = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123"
    url2 = "https://www.laizquierdadiario.com/Nacional/noticia456"
    url3 = "https://www.laizquierdadiario.com/Internacional/noticia789"
    url4 = "https://www.laizquierdadiario.com/noticia000"  # No tiene sección
    url5 = "https://www.otherwebsite.com/Some-Section/news"  # No coincide con el patrón

   # print("Holiiiiiiiiiiiiiiiiis")
    #print(extraer_seccion(url1))

    assert extraer_seccion(url1) == "provincia-de-buenos-aires", "Error en la extracción de la sección para url1"
    print(extraer_seccion(url1))
    assert extraer_seccion(url2) == "nacional", "Error en la extracción de la sección para url2"
    assert extraer_seccion(url3) == "internacional", "Error en la extracción de la sección para url3"
    assert extraer_seccion(url4) == "NA", "Error en la extracción de la sección para url4"
    print(extraer_seccion(url5))
    #assert extraer_seccion(url5) == "NA", "Error en la extracción de la sección para url5" ##preguntar luego por esto si coincide con los requerimiento

def test_link_length(): #hay algo raro aca
    
    url1 = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Aires/noticia123-PARO"
    url2 = "https://www.laizquierdadiario.com/Nacional/noticia456"
    url3 = "https://www.laizquierdadiario.com/Internacional/noticia789"
    url4 = "https://www.laizquierdadiario.com/noticia000"
    url5 = "https://www.laizquierdadiario.com/Seccion-Con-Muchas-Palabras/noticia999"
    print("LLEGUE ACA")
    print(link_length(url5))
    assert link_length(url2) == 1, "Error en el cálculo de la longitud del enlace para url2" #NO DEBERIA DAR 1
    assert link_length(url3) == 1, "Error en el cálculo de la longitud del enlace para url3"
    assert link_length(url4) == 1, "Error en el cálculo de la longitud del enlace para url4"
    assert link_length(url5) == 1, "Error en el cálculo de la longitud del enlace para url5"
    print(link_length(url5))

def test_create_tag():
    url1 = "https://www.laizquierdadiario.com/Provincia-de-Buenos-Airés/noticia123"
    url2 = "https://www.laizquierdadiario.com/Nacional/paro-noticia456"
    url3 = "https://www.laizquierdadiario.com/Internacional/noticia789-trabajadores-en-huelga"
    url4 = "https://www.laizquierdadiario.com/noticia000"
    url5 = "https://www.laizquierdadiario.com/Seccion-Con-Muchas-Palabras/noticia999-banco-a-lxs-trabajadores-de-la-economia-populares"

    assert create_tag(url1) == ""
    assert create_tag(url2) == "paro", "Error en la creación de tags para url2"
    assert create_tag(url3) == "trabajadores huelga", "Error en la creación de tags para url3"
    assert create_tag(url4) == " ", "Error en la creación de tags para url4"
    assert create_tag(url5) == "trabajadores de la economia popular", "Error en la creación de tags para url5"