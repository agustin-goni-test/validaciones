import os
from typing import Optional
import requests
import json

class PluttoClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        endpoint_validation_by_tin: str,
        endpoint_validation: str,
        endpoint_validation_for_wl: str,
        endpoint_watchlists: str,
        debug: bool
    ):
        self.base_url = base_url
        self.token = token
        self.endpoint_validation_by_tin = endpoint_validation_by_tin
        self.endpoint_validation = endpoint_validation
        self.endpoint_validation_for_wl = endpoint_validation_for_wl
        self.endpoint_watchlists = endpoint_watchlists
        self.debug = True if debug == "true" else False


    def obtain_validation_by_tin(self, rut: str) -> tuple[bool, str]:

        found = False

        # Build the required URL
        url = self.base_url + self.endpoint_validation_by_tin + rut

        if self.debug:
            print("Ejecutando validación por RUT...")
            print(url)

        # Add headers
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.token}'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            if self.debug: print("Informe no encotrado, retornará False")
            found = False
            return found, None
        
        elif response.status_code == 200:
            if self.debug: print("Informe encontrado, retornará JSON")
            found = True
            report = response.json()
            return found, report
        
        else:
            # Raise exception
            raise RuntimeError(
            f"Unexpected response from Plutto API: "
            f"status={response.status_code}, body={response.text}"
            )
        

    def obtain_validation(self, rut: str) -> tuple[bool, str]:
        
        # Build the required URL
        url = self.base_url + self.endpoint_validation

        # Add headers
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'authorization': f'Bearer {self.token}'
        }
        
        payload = {
            "entity_validation":{
            "country": "CL",
            "tin": f"{rut}"
            }
        }

        if self.debug:
            print(url)
            print(payload)

        response = requests.post(url=url, headers=headers, json=payload)

        report = response.json()
        id = report.get('id', None)

        if response.status_code == 201:
            if self.debug: print("Creación del informe exitosa...")
            return True, id
        
        elif response.status_code == 422:
            print("Error en el request. No se puede procesar.")
            return False, None
        
        else:
            print("Algo salió mal...")
            raise RuntimeError(
            f"Unexpected response from Plutto API: "
            f"status={response.status_code}, body={response.text}"
            )
        
        
    def obtain_validation_by_id(self, id: str) -> tuple[bool, str]:
        '''Obtain validation by ID'''

        found = False

        # Build the required URL
        url = self.base_url + self.endpoint_validation + "/" + id

        if self.debug:
            print("Ejecutando validación por ID...")
            print(url)

        # Add headers
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.token}'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            if self.debug: print("Informe no encontrado, retornará False")
            found = False
            return found, None
        
        elif response.status_code == 200:
            if self.debug: print("Informe encontrado, retornará JSON")
            found = True
            report = response.json()
            return found, report
        
        else:
            raise RuntimeError(
                f"Unexpected response from Plutto API: "
                f"status={response.status_code}, body={response.text}"
            )


    def obtain_watchlists(self, id: str) -> tuple[bool, dict]:
        '''Obtain watchlists for a given ID'''

        found = False

        # Build the required URL
        url = self.base_url + self.endpoint_validation_for_wl + id + self.endpoint_watchlists

        if self.debug:
            print("Ejecutando validación por ID...")
            print(url)

        # Add headers
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {self.token}'
        }

        response = requests.get(url, headers=headers)

        # If the report was found, return true and the report
        if response.status_code == 200:
            found = True
            report = response.json()
            return found, report
        
        elif response.status_code == 500:
            print(f"Error 500 en request para ID {id}.")
            return False, None

        
        else:
            raise RuntimeError(
                f"Unexpected response from Plutto API: "
                f"status={response.status_code}, body={response.text}"
            )
    


# Instance of the client
_plutto_client_instance: Optional[PluttoClient] = None

# Method to get or construct the client
def get_plutto_client() -> PluttoClient:
    """PluttoClient singleton implementation"""
    global _plutto_client_instance

    if _plutto_client_instance is None:
        base_url = os.getenv("BASE_URL_PLUTTO")
        token = os.getenv("TOKEN_PLUTTO")
        endpoint_validation_by_tin = os.getenv("ENDPOINT_VALIDATION_BY_TIN")
        endpoint_validation = os.getenv("ENDPOINT_VALIDATION")
        endpoint_validation_for_wl = os.getenv("ENDPOINT_VALIDATION_FOR_WL")
        endpoint_watchlists = os.getenv("ENDPOINT_WATCHLISTS")
        debug = os.getenv("DEBUG")

        # Check for missing environment variables
        if None in (
            base_url,
            token,
            endpoint_validation_by_tin,
            endpoint_validation,
            endpoint_validation_for_wl,
            endpoint_watchlists,
        ):
            missing = []
            if base_url is None: missing.append("BASE_URL_PLUTTO")
            if token is None: missing.append("TOKEN_PLUTTO")
            if endpoint_validation_by_tin is None: missing.append("ENDPOINT_VALIDATION_BY_TIN")
            if endpoint_validation is None: missing.append("ENDPOINT_VALIDATION")
            if endpoint_validation_for_wl is None: missing.append("ENDPOINT_VALIDATION_FOR_WL")
            if endpoint_watchlists is None: missing.append("ENDPOINT_WATCHLISTS")

            raise RuntimeError(
                f"Missing environment variables: {', '.join(missing)}\n"
                "Please check your .env file or environment configuration."
            )

        _plutto_client_instance = PluttoClient(
            base_url=base_url,
            token=token,
            endpoint_validation_by_tin=endpoint_validation_by_tin,
            endpoint_validation=endpoint_validation,
            endpoint_validation_for_wl=endpoint_validation_for_wl,
            endpoint_watchlists=endpoint_watchlists,
            debug=debug
        )

    return _plutto_client_instance
