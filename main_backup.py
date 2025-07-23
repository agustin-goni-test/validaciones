import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Optional, List, Dict, Any
from direcciones import DireccionPersonaNatural, DireccionPersonaJuridica
from contact_data import EmailJuridica, PhoneNumberJuridica, PhoneNumberNatural
from dotenv import load_dotenv
import os
import sys
import select
import time

load_dotenv()

def main():
    # Take a file with this name as a starting point
    # Will output to a different file
    file_path = 'Datos clientes.xlsx'

    # Initialize tokens
    TOKEN_PERSONA_NATURAL = ""
    TOKEN_PERSONA_JURIDICA = ""

    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Print the first few rows to verify
    print(df.head())
    print("\n")

    # Verify the number of data rows in the file
    print(f"Número de clientes en la lista: {len(df)} ")

    # Categorizar a todas las personas como naturales o jurídicas
    categoria_persona(df)

    print("Grabando datos de categorías de personas")
    df.to_excel('Datos clientes completos.xlsx', index=False)

    ##################################################
    # Obtain tokens for the service, with two options:
    # 1. Use a preconfigured token (env)
    # 2. Use a method that dynamically obtains the token

    # Dynamic tokens
    # TOKEN_PERSONA_NATURAL = obtener_token_persona_natural()
    # TOKEN_PERSONA_JURIDICA = obtener_token_persona_juridica()
    
    # Static (env) tokens        
    TOKEN_PERSONA_NATURAL = os.getenv("TOKEN_INTERNO_NATURAL")
    TOKEN_PERSONA_JURIDICA = os.getenv("TOKEN_INTERNO_JURIDICA")

    ####################################################

    ####################################################
    # This commented code allows to test some elements of the solution

    # RUT = "764311612"

    # response_natural = obtener_informe_platinum(TOKEN_PERSONA_NATURAL, "176402423")
    # response_juridica = obtener_informe_comercial(TOKEN_PERSONA_JURIDICA, RUT)

    # print("Persona natural...")
    # phone_numbers_natural = obtener_telefono_persona_natural(response_natural)
    # email_natural = obtener_email_personal_natural(response_natural)

    # for num in phone_numbers_natural:
    #     print(f"Teléfono: {num.telephone}")

    # print (f"Email: {email_natural}")

    # print("\nPersona jurídica...")
    # phone_numbers_juridica = obtener_telefono_persona_juridica(response_juridica)
    # email_juridica = obtener_email_persona_juridica(response_juridica)

    # for num in phone_numbers_juridica:
    #     print(f"Teléfono: {num.subtype} - +{num.country_code}-{num.area_code}-{num.number}")

    # for email in email_juridica:
    #     print(f"email: {email.email}")

    # print("\n\n")
    # print("Obteniendo direcciones...")

    # direcciones = obtener_direcciones_persona_natural(response_natural)
    # print(f"Cantidad de direcciones persona natural: {len(direcciones)}")

    # for direccion in direcciones:
    #     # print(f"{direccion.street} {direccion.number}, {direccion.communes}, {direccion.city}, {direccion.region}")
    #     address = address_to_string(direccion)
    #     print(address)

    # dir_jur = obtener_direcciones_persona_juridica(response_juridica)
    # print(f"Cantidad de direcciones persona jurídica: {len(dir_jur)}")

    # for direccion in dir_jur:
    #     address = address_to_string(direccion)
    #     print(address)

 
    # Block size to use in the processing of the file
    block_size = 10

    # Timeout for continuation prompt (if the user doesn't answer, it will continue)
    timeout_lapse = 10

    # Size of the data frame
    total_rows = len(df)

    # Start position. Can be useful if the file is already partially processed.
    start_position = 0

    # Go through the whole file, block by block
    for start in range(start_position, total_rows, block_size):

        # Compute the last index to processm make sure it doesn't exceed the size
        end = min(start + block_size - 1, total_rows - 1)

        # Process the customers in the block
        df = procesar_direcciones(
            df,
            TOKEN_PERSONA_NATURAL,
            TOKEN_PERSONA_JURIDICA,
            start,
            end
        )

        # Write the results of the processed block to the output file
        print(f"Escribiendo bloque entre filas {start} y {end} en archivo Excel... \n")
        df.to_excel('Datos clientes completos.xlsx', index=False)
    
        # Prompt user to continue
        if end < total_rows -1:
            print(f"Continuar con el siguiente bloque? (automático en {timeout_lapse} segundos) (s/n):")

            # Use select (works on Linux or Mac) to capture standard input.
            # The select function monitors I/O streams and signals which ones
            # are ready for reading, writing, or have errors. General syntax:
            # readable, writable, errored = select.select(read_list, write_list, error_list, timeout)
            ready, _, _ = select.select([sys.stdin], [], [], timeout_lapse)

            # If there is user input (with ENTER)
            if ready:
                # Obtain input, strip and turn to lowercase
                user_input = sys.stdin.readline().strip().lower()

                # IF "no", interrupt processing
                if user_input == "n":
                    print(f"Proceso interrumpido por el usuario. Última fila procesada: {end}")
                    exit()
                
                # If "yes", continue
                elif user_input == "s":
                    print("Usuario seleccionó continuar...")
                
                # If anything else, also continue
                else:
                    print(f"Opción inválida. Continuar por defecto...")             
            else:
                print("No hubo respuesta dentro del tiempo permitido. Continuando por defecto...")


def address_to_string(direccion) -> str:
    '''Obtain correctly formatted addresses to include in the output.
    Works for both classes of customer.'''
    if isinstance(direccion, DireccionPersonaNatural):
        return(
            f"{direccion.street} {direccion.number}, "
            f"{direccion.communes}, "
            f"{direccion.city}, "
            f"{direccion.region}"
        )
    elif isinstance(direccion, DireccionPersonaJuridica):
        return (
            f"{direccion.addressType} - "
            f"{direccion.street} {direccion.number}, "
            f"{direccion.communes}, "
            f"{direccion.city}, "
            f"{direccion.region}"
        ) 
            
    else:
        return "Dirección desconocida"


def obtener_informe_platinum(token: str, rut: str) -> dict:
    '''Obtain report for person'''

    # Point to report API URL
    url = os.getenv("URL_REPORT")

    # Add headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Add payload in a specific format. Only the RUT varies
    payload = {
        "applicants": {
            "primaryConsumer": {
                "personalInformation": {
                    "chileanRut": rut,
                    "chileanSerialNumber": "10848699"
                }
            }
        },
        "productData": {
            "billTo": "CL000724B001",
            "shipTo": "CL000724B001S001",
            "productName": "CLPLAT",
            "productOrch": "PLATV1",
            "configuration": "Config",
            "customer": "CLPLATISWITCH",
            "model": "PLATISWITCH"
        }
    }

    # Send request and raise for status
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    # Obtain response and return
    result = response.json()
    return result


def obtener_informe_comercial(token: str, rut: str) -> dict:
    '''Obtain report for corporation'''
    
    # Point to report API URL
    url = os.getenv("URL_REPORT")

    # Add headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Add payload in a specific format. Only the RUT varies
    payload = {
        "applicants": {
            "primaryConsumer": {
                "personalInformation": {
                    "chileanRut": rut  # assuming rut is defined elsewhere
                }
            }
        },
        "productData": {
            "billTo": "CL000429B001",
            "shipTo": "CL000429B001S001",
            "productName": "CLREPORTEEMPRESARIAL",
            "productOrch": "REPORTEEMPRESARIAL",
            "configuration": "Config",
            "customer": "CLREISWITCH",
            "model": "ISWITCH"
        }
    }

    # Send request and raise for status
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    # Obtain response and return
    result = response.json()
    return result


def obtener_token_persona_natural() -> str:
    '''Obtain token that allows to request a report for a person'''
    
    # Point to token acquisition URL
    url = os.getenv("URL_TOKEN")
    
    # Obtain credentials for "NATURAL"
    user_natural = os.getenv("USER_NATURAL")
    password_natural = os.getenv("PASSWORD_NATURAL")

    # Basic authentication (user and password)
    auth = HTTPBasicAuth(user_natural, password_natural)
    
    # Add headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Add data for the POST
    data = {
        'scope': 'https://api.latam.equifax.com/datos-comerciales/transaction',
        'grant_type': 'client_credentials'
    }

    # Call the service
    response = requests.post(url, auth=auth, headers=headers, data=data)
    
    # Raise an error if the request failed
    response.raise_for_status()

    # Extract the access token
    token = response.json().get('access_token')

    if not token:
        raise ValueError("No pudo obtener un token.")

    return token


def obtener_token_persona_juridica() -> str:
    '''Obtain token that allows to request a report for a corporation'''
    
    # Point to token acquisition URL
    url = os.getenv("URL_TOKEN")
    
    # Obtain credentials for "JURIDICA"
    user_juridica = os.getenv("USER_JURIDICA")
    password_juridica = os.getenv("PASSWORD_JURIDICA")

    # Basic authentication (user and password)
    auth = HTTPBasicAuth(user_juridica, password_juridica)
    
    # Add headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Add data for the POST
    data = {
        'scope': 'https://api.latam.equifax.com/datos-comerciales/transaction',
        'grant_type': 'client_credentials'
    }

    # Call the service
    response = requests.post(url, auth=auth, headers=headers, data=data)
    
    # Raise an error if the request failed
    response.raise_for_status()

    # Extract the access token
    token = response.json().get('access_token')

    if not token:
        raise ValueError("No pudo obtener un token.")

    return token

def categoria_persona(df):
    '''Categorizes customers as persons or corporations'''
    # Add a new column "PERSONA" based on whether each RUT is juridical or natural
    df['PERSONA'] = df.iloc[:, 0].apply(
        lambda rut: 'JURIDICA' if is_persona_juridica(rut) else 'NATURAL'
    )

    print("Clasificamos todos los clientes en persona natural o jurídica.")
    


def is_persona_juridica(rut: str) -> bool:
    '''Determina si el RUT recibido es de una persona jurídica.
    Si lo es retorna true, de lo contrario false'''
    try:
        # Get the numeric part before the hyphen
        numeric_part = rut.split('-')[0]
        number = int(numeric_part)
        
        # Compare to 50000000 (rule of thumb for the type of customer)
        return number > 50000000
    
    except (ValueError, AttributeError, IndexError):
        # In case the RUT is malformed or None
        print(f"El valor {rut} no pudo ser procesado. Hubo un error.")
        return False


def obtener_direcciones_persona_natural(response: Dict[str, Any]) -> List[DireccionPersonaNatural]:
    '''Retrive list of addresses from report for a person.
    Returns a list of class DireccionPersonaNatural.'''

    try:
        # Get the addresses from the JSON reponse
        raw_addresses = (
                response
                .get("platinum360", {})
                .get("getInformePlatinum360Response", {})
                .get("response", {})
                .get("Behavior", {})
                .get("Contactability", {})
                .get("Addresses", {})
                .get("AddressesType", [])
            )
        
        # Parse as objects
        direcciones = [DireccionPersonaNatural.from_dict(addr) for addr in raw_addresses]

        # return list
        return direcciones
    
    except KeyError:
        # If path doesn't exist, return empty list
        return[]
    

def obtener_direcciones_persona_juridica(response: Dict[str, Any]) -> List[DireccionPersonaJuridica]:
    '''Retrive list of addresses from report for a corporation.
    Returns a list of class DireccionPersonaJuridica.'''
    
    try:
        # Get the addresses from the JSON reponse
        raw_addresses = (
            response
                .get("data", {})
                .get("commercialData",{})
                .get("behavior",{})
                .get("contactability", {})
                .get("contactsDataDetail", {})
                .get("addresses", {})
                .get("commercialAddresses", {})
        )

        # Parse as objects and return the list
        return [DireccionPersonaJuridica.from_dict(addr) for addr in raw_addresses]
    
    except KeyError:
        # If path doesn't exist, return empty list
        return[]


def obtener_telefono_persona_juridica(response: Dict[str, Any]) -> List[PhoneNumberJuridica]:
    '''Retrive list of phone numbers from report for a corporation.
    Returns a list of class PhoneNumberJuridica.'''
    
    try:
        # Get the numbers from the JSON reponse
        raw_numbers = (
            response
            .get("data", {})
            .get("commercialData",{})
            .get("behavior",{})
            .get("contactability", {})
            .get("contactsDataDetail", {})
            .get("telephones", {})
            .get("referenceData", {})
        )

        # Parse as objects and return the list
        return [PhoneNumberJuridica.from_dict(num) for num in raw_numbers]
    
    except KeyError:
        # If path doesn't exist, return empty list
        return []


def obtener_telefono_persona_natural(response: Dict[str, Any]) -> List[PhoneNumberNatural]:
    '''Retrive list of phone numbers from report for a person.
    Returns a list of class PhoneNumberNatural.'''
    
    try:
        # Get the numbers from the JSON reponse
        raw_numbers = (
                response
                .get("platinum360", {})
                .get("getInformePlatinum360Response", {})
                .get("response", {})
                .get("Behavior", {})
                .get("Contactability", {})
                .get("Telephones", {})
                .get("TelephonesType", [])
            )
        
        # Parse as objects and return the list
        return [PhoneNumberNatural.from_dict(num) for num in raw_numbers]

    except KeyError:
        # If path doesn't exist, return empty list
        return []


def obtener_email_persona_juridica(response: Dict[str, Any]) -> List[EmailJuridica]:
    '''Retrive list of emails from report for a corporation.
    Returns a list of class EmailJuridica.'''
    
    try:
        # Get the emails from the JSON reponse
        raw_emails = (
            response
            .get("data", {})
            .get("commercialData",{})
            .get("behavior",{})
            .get("contactability", {})
            .get("contactsDataDetail", {})
            .get("emails", {})
            .get("referenceData", {})
        )

        # Parse as objects and return the list
        return [EmailJuridica.from_dict(email) for email in raw_emails]
    
    except KeyError:
        # If path doesn't exist, return empty list
        return []


def obtener_email_personal_natural(response: Dict[str, Any]) -> str:
    '''Retrive list of emails from report for a corporation.
    Returns a string.'''
    
    try:
        # Get the email from the JSON reponse (always one and no more)
        email = (
            response
            .get("platinum360", {})
            .get("getInformePlatinum360Response", {})
            .get("response", {})
            .get("Behavior", {})
            .get("Other", {})
            .get("Email", "")
        )

        # Return as string
        return email
    
    except KeyError:
        # If path doesn't exist, return empty string
        return ""
   

def procesar_direcciones(
        df: pd.DataFrame,
        token_natural: str,
        token_juridico: str,
        start: int = 0,
        end: Optional[int] = None,
    ) -> pd.DataFrame:
    '''This method is the one that uses the reports to add information
    to the output file.
    
    The processing is done by blocks, from start to end (parameters).
    It also takes a Data Frame and the required tokens'''
    
    # Size of the whole file to process
    size = len(df)
    print(f"\nLa lista de comercios tiene {size} registros")

    # Keep a count of the maximum number of addresses for any customer
    max_addresses = 0

    # Store all addresses found
    all_addresses = []
    

    # If there is no end position, use the end of the DataFrame
    if end is None or end > len(df):
        end = len(df)

    print(f"\nEmpezando en la posición {start} hasta la posición {end} \n")

    # Check if these columns exist. If not they need to be added.
    required_columns = ["Procesado", "Teléfono", "Email"]

    if not all(col in df.columns for col in required_columns):
        # Create the columns; determine where to insert
        direccion_cols = [col for col in df.columns if col.lower().startswith("direccion")]
        insert_at = df.columns.get_loc(direccion_cols[0]) if direccion_cols else len(df.columns)

        # Add the columns in reverse
        for col_name in reversed(required_columns):
            if col_name not in df.columns:
                default_value = 0 if col_name == "Procesado" else ""
                df.insert(loc=insert_at, column=col_name, value=default_value)


    # Traverse the corresponding block to process each customer
    for idx in range(start, end + 1):
        row = df.iloc[idx]
        rut = row["Rut"]
        RUT_para_consulta = rut.replace("-", "")
        type = row["PERSONA"]

        # Máximum number of retries for the service (in case of an HTTP 500 code)
        max_retries = 5

        # Time to wait in case a retry is necessary
        retry_delay = 2

        phone_string = ""
        email_string = ""

        print(f"Fila {idx} - Consultaremos informe para rut {rut}, comercio tipo persona {type}")

        # Loop for as long as there are available retries
        for attempt in range(max_retries):
            try:
                if type == "NATURAL":                    
                    # Obtain the corresponding report
                    response = obtener_informe_platinum(token_natural, RUT_para_consulta)
                    
                    # Obtain all the addresses in this report
                    direcciones = obtener_direcciones_persona_natural(response)
                    # print("Direcciones obtenidas con éxito.")
                    
                    # Obtain phone numbers and email
                    phone_numbers = obtener_telefono_persona_natural(response)
                    email_string = obtener_email_personal_natural(response)

                    # Prepare phone number string (email is already set as string)
                    # phone_string = ""
                    for num in phone_numbers:
                        phone_string += f"{num.telephone}; "
                    
                    # print("Datos de contacto obtenidos con éxito.")
                
                elif type == "JURIDICA":
                    # Obtain the corresponding report
                    response = obtener_informe_comercial(token_juridico, RUT_para_consulta)
                    
                    # Obtain all the addresses in this report
                    direcciones = obtener_direcciones_persona_juridica(response)
                    # print("Direcciones obtenidas con éxito")
                    
                    # Obtain phone numbers and email
                    phone_numbers = obtener_telefono_persona_juridica(response)
                    email = obtener_email_persona_juridica(response)

                    # Prepare strings for phone number and email
                    # phone_string = ""
                    for num in phone_numbers:
                        phone_string += f"{num.subtype}: +{num.country_code}-{num.area_code}-{num.number}; "

                    if email:
                        email_string = f"{email[0].email}"
                    else:
                        email_string = ""
                    
                    # print("Datos de contacto obtenidos con éxito.")
                
                else:
                    direcciones = []
                break # Success, break out of the loop
                
            except requests.exceptions.HTTPError as e:
                print(f"Ocurrió un error en intento {attempt + 1} de {max_retries} al servicio con rut {rut}: {e}")
                
                # If there are available retries, sleep and retry. Otherwise, mark as failed
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:                    
                    df.at[idx, "Procesado"] = 0
                    df.at[idx, "Teléfono"] = ""
                    df.at[idx, "Email"] = ""
                    all_addresses.append([])
                    break 
            
            except Exception as e:
                print(f"Error desconocido al procesar cliente {rut}: {e}")
                df.at[idx, "Procesado"] = 0
                df.at[idx, "Teléfono"] = ""
                df.at[idx, "Email"] = ""
                all_addresses.append([])
                break

        # Obtain a string representation of the address
        # (depending on type)
        string_direcciones = [address_to_string(addr) for addr in direcciones]

        if string_direcciones or direcciones == []:
            df.at[idx, "Procesado"] = 1

        df.at[idx, "Teléfono"] = phone_string if phone_string else "S/I"
        df.at[idx, "Email"] = email_string if email_string else "S/I"

        print(f"Direcciones encontradas para comercio {rut}: {len(string_direcciones)}")
        print(f"Datos de contacto: {email_string} -- {phone_string}")
       
        max_addresses = max(max_addresses, len(string_direcciones))
        all_addresses.append(string_direcciones)

    # Add new columns to the DataFrame if they don't exist
    for i in range(max_addresses):
        col_name = f"direccion{i+1}"
        if col_name not in df.columns:
            df[col_name] = ""


    # Fill in the processed rows
    for local_idx, global_idx in enumerate(range(start, end + 1)):
        string_direcciones = all_addresses[local_idx]
        for i, val in enumerate(string_direcciones):
            df.at[global_idx, f"direccion{i+1}"] = val

    return df




if __name__ == '__main__':
    main()