from dotenv import load_dotenv
from clients.equifax_client import get_equifax_client
from clients.plutto_client import get_plutto_client
from clients.gesintel_client import get_gestintel_client
import json
from preparation import ValidationControlFlow
from library.plutto_components import WatchlistResponse
from controllers.plutto_controller import PluttoController
import requests

load_dotenv()

def main():

    # Test if the Equifax client is working OK
    # test_equifax_client()

    # Test if the Plutto client is working OK
    # test_plutto_client_by_tin()
    # test_plutto_client_validation()
    # test_plutto_client_validation_by_id()
    # test_plutto_client_watchlists()
    # test_plutto_watchlist_response()

    ######################################
    # Test methods related to GESINTEL
    ######################################

    test_get_aml_result()
    # test_get_aml_risk()
    # test_get_aml_report()
    # test_get_flag_results()
    # test_get_entity_data()
    # test_get_entity_record()


    print("\nThe end")


#############################################################
#
# Start GESINTEL tests
#
#############################################################

def test_get_aml_result():
    '''Test getAMLResult method by using GET'''

    rut = "771253296"

    try:
        gesintel_client = get_gestintel_client()
    
    except Exception as e:
        print("Error obteniendo el cliente de GESINTEL")
        print(f"{str(e)}")
        return

    try:
        found, report = gesintel_client.get_aml_result(rut)

        if found:
            print(f"El reporte para RUT {rut} fue obtenido con éxito...")
            print(json.dumps(report, indent=4))

    except requests.HTTPError as e:
        print(f"Error en la comunicación con la API Gesintel: {e}")


def test_get_aml_risk():
    '''Test getAMLResult method by using GET'''

    rut = "73426464"

    try:
        gesintel_client = get_gestintel_client()
    
    except Exception as e:
        print("Error obteniendo el cliente de GESINTEL")
        print(f"{str(e)}")
        return

    try:
        found, report = gesintel_client.get_aml_risk(rut)

        if found:
            print(f"El reporte para RUT {rut} fue obtenido con éxito...")
            print(json.dumps(report, indent=4))

    except requests.HTTPError as e:
        print(f"Error en la comunicación con la API Gesintel: {e}")
    

def test_get_aml_report():
    '''Test getAMLReport method by using GET'''

    rut = "73426464"

    try:
        gesintel_client = get_gestintel_client()
    
    except Exception as e:
        print("Error obteniendo el cliente de GESINTEL")
        print(f"{str(e)}")
        return

    try:
        found, report = gesintel_client.get_aml_report(rut)

        if found:
            print(f"El reporte para RUT {rut} fue obtenido con éxito...")
            print(json.dumps(report, indent=4))

    except requests.HTTPError as e:
        print(f"Error en la comunicación con la API Gesintel: {e}")


def test_get_flag_results():
    '''Test getFlagResults method by using GET'''

    rut = "73426464"

    try:
        gesintel_client = get_gestintel_client()
    
    except Exception as e:
        print("Error obteniendo el cliente de GESINTEL")
        print(f"{str(e)}")
        return

    try:
        found, report = gesintel_client.get_flag_results(rut)

        if found:
            print(f"El reporte para RUT {rut} fue obtenido con éxito...")
            print(json.dumps(report, indent=4))

    except requests.HTTPError as e:
        print(f"Error en la comunicación con la API Gesintel: {e}")


def test_get_entity_data():
    '''Test getEntityData method by using GET'''

    rut = "73426464"

    try:
        gesintel_client = get_gestintel_client()
    
    except Exception as e:
        print("Error obteniendo el cliente de GESINTEL")
        print(f"{str(e)}")
        return

    try:
        found, report = gesintel_client.get_entity_data(rut)

        if found:
            print(f"El reporte para RUT {rut} fue obtenido con éxito...")
            print(json.dumps(report, indent=4))

    except requests.HTTPError as e:
        print(f"Error en la comunicación con la API Gesintel: {e}")


def test_get_entity_record():
    '''Test getEntityReport method by using GET'''

    rut = "73426464"

    try:
        gesintel_client = get_gestintel_client()
    
    except Exception as e:
        print("Error obteniendo el cliente de GESINTEL")
        print(f"{str(e)}")
        return

    try:
        found, report = gesintel_client.get_entity_record(rut)

        if found:
            print(f"El reporte para RUT {rut} fue obtenido con éxito...")
            print(json.dumps(report, indent=4))

    except requests.HTTPError as e:
        print(f"Error en la comunicación con la API Gesintel: {e}")


#############################################################
#
# Start Plutto tests
#
#############################################################


def test_plutto_watchlist_response():
    '''Test watchlist method'''
    
    plutto_client = get_plutto_client()
    
    watchlist = None

    found, watchlist_json = plutto_client.obtain_watchlists("evl_a133b8bb2f8ea61a")


    if found:
        watchlist_response = WatchlistResponse(watchlist_json)
        watchlist = watchlist_response.watchlists[0] if watchlist_response.watchlists else None
        print(f"Watchlist obtenida con éxito para {watchlist.watchlistable_name}.")
        
        # Obtain the number of hits in the variable watchlist
        hits = len(watchlist.hits[0].list_matches)
        print(f"Número de hits: {hits}")


def test_plutto_client_by_tin():
    
    plutto_client = get_plutto_client()
    
    rut = "76431161-2"
    found, report = plutto_client.obtain_validation_by_tin(rut)

    if found:
        print("El informe para el comercio fue obtenido con éxito.")
        print(json.dumps(report, indent=4))
    else:
        print("El informe no estaba disponible en el servicio.")


def test_plutto_client_validation():
    
    plutto_client = get_plutto_client()
    rut = "76934499-3"

    created = plutto_client.obtain_validation(rut)

    if created:
        found, report = plutto_client.obtain_validation_by_tin(rut)
        if found:
            print(json.dumps(report, indent=4))
        else:
            print("Error al obtener informe")


def test_plutto_client_validation_by_id():

    plutto_client = get_plutto_client()
    id = "evl_b92418dca42f4238"

    found, report = plutto_client.obtain_validation_by_id(id)

    if found:
        print("El informe fue obtenido con éxito.")
        print(json.dumps(report, indent=4))
    else:
        print("El informe no estaba disponible en el servicio.")


def test_plutto_client_watchlists():
    plutto_client = get_plutto_client()
    id = "evl_b92418dca42f4238"

    found, report = plutto_client.obtain_watchlists(id)

    if found:
        print("El informe de watchlists fue obtenido con éxito.")
        print(json.dumps(report, indent=4))
    else:
        print("El informe de watchlists no estaba disponible en el servicio.")


def test_equifax_client():
    '''Method to test the Equifax client.
    Creates both tokens and gets reports.'''
    print("Método de pruebas para cliente de Equifax")

    # Creating client
    equifax_client = get_equifax_client()
    if equifax_client:
        print(f"Cliente creado con éxito. URL de request: {equifax_client.request_url}")

    # Set authorization method (fixed or dynamic)
    print("Obtaining dynamic tokens")
    equifax_client.set_token_origin("auth")

    if equifax_client.token_natural:
        print("Token para consulta de persona natural OK.")

    if equifax_client.token_juridica:
        print("Token para consulta de persona jurídica OK.")

    rut_natural = "176402423"
    rut_juridico = "764311612"

    informe_juridica = equifax_client.obtain_report_corporation(rut_juridico)
    informe_natural = equifax_client.obtener_report_person(rut_natural)

    if informe_juridica:
        print("\nPersona jurídica:")
        print(json.dumps(informe_juridica, indent=4))

    if informe_natural:
        print("\nPersona natural:")
        print(json.dumps(informe_natural, indent=4))
    
    print("\nFin de la prueba")


if __name__ == '__main__':
    main()
