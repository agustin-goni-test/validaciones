from dotenv import load_dotenv
from clients.equifax_client import get_equifax_client
from clients.plutto_client import get_plutto_client
import json
from preparation import ValidationControlFlow

load_dotenv()

def main():

    # Test if the Equifax client is working OK
    # test_equifax_client()

    # Test if the Plutto client is working OK
    # test_plutto_client_by_tin()
    # test_plutto_client_validation()
    # test_plutto_client_validation_by_id()
    # test_plutto_client_watchlists()

    validation_control_flow()

    print("\nThe end")


def validation_control_flow():

    # Initialize the validation control flow with the Excel file path
    excel_file = "Datos clientes.xlsx"
    validation_flow = ValidationControlFlow(excel_file)

    if validation_flow.df.empty:
        print("El Excel no contiene datos.")
        return
    else:
        print(f"Datos cargados correctamente con {len(validation_flow.df)} filas.")
        validation_flow.prepare_data()

    # Perform operations on the DataFrame
    # For example, you can modify the DataFrame here
    # validation_flow.df['new_column'] = 'value'



    # Save the DataFrame back to the Excel file
    validation_flow.save_to_excel()


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
