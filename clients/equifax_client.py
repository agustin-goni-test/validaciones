from dotenv import load_dotenv
import os
import json
import requests
from typing import Optional
from requests.auth import HTTPBasicAuth

class EquifaxClient:
    def __init__(
            self,
            login_url: str,
            request_url: str,
            user_natural: str,
            password_natural: str,
            user_juridica: str,
            password_juridca: str,
            token_natural: str,
            token_juridica: str,
            scope: str
    ):
        self.login_url = login_url
        self.request_url = request_url
        self.user_natural = user_natural
        self.password_natural = password_natural
        self.user_juridica = user_juridica
        self.password_juridica = password_juridca
        self.token_natural = token_natural
        self.token_juridica = token_juridica
        self.scope = scope


    def obtain_token_person(self) -> str:
        '''Obtain token that allows to request a report for a person'''
        
        # Basic authentication (user and password)
        auth = HTTPBasicAuth(self.user_natural, self.password_natural)
        
        # Add headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Add data for the POST
        data = {
            'scope': f'{self.scope}',
            'grant_type': 'client_credentials'
        }

        # Call the service
        response = requests.post(self.login_url, auth=auth, headers=headers, data=data)
        
        # Raise an error if the request failed
        response.raise_for_status()

        # Extract the access token
        token = response.json().get('access_token')

        if not token:
            raise ValueError("No se pudo obtener un token.")

        return token


    def obtain_token_corporation(self) -> str:
        '''Obtain token that allows to request a report for a corporation'''
        

        # Basic authentication (user and password)
        auth = HTTPBasicAuth(self.user_juridica, self.password_juridica)
        
        # Add headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Add data for the POST
        data = {
            'scope': f'{self.scope}',
            'grant_type': 'client_credentials'
        }

        # Call the service
        response = requests.post(self.login_url, auth=auth, headers=headers, data=data)
        
        # Raise an error if the request failed
        response.raise_for_status()

        # Extract the access token
        token = response.json().get('access_token')

        if not token:
            raise ValueError("No pudo obtener un token.")

        return token


    def set_token_origin(self, origin: str = "env") -> bool:
        '''Determine where to get the tokens from. Options are:
        
        'env': reads them from the environment variables (fixed)
        'auth': authenticates with user and password (dynamic)'''
        
        if origin == "env":
            self.token_natural = os.getenv("TOKEN_INTERNO_NATURAL")
            self.token_juridica = os.getenv("TOKEN_INTERNO_JURIDICA")
        
        elif origin == "auth":
            self.token_natural = self.obtain_token_person()
            self.token_juridica = self.obtain_token_corporation()

        else:
            raise RuntimeError(
                f"Option {origin} not recognized for origin."
            )
        

    def obtain_report_corporation(self, rut: str) -> dict:
        '''Obtain report for corporation'''
        
        # Point to report API URL
        url = os.getenv("URL_REPORT")

        # Add headers
        headers = {
            "Authorization": f"Bearer {self.token_juridica}",
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
        response = requests.post(self.request_url, headers=headers, json=payload)
        response.raise_for_status()

        # Obtain response and return
        result = response.json()
        return result



_equifax_client_instance: Optional[EquifaxClient] = None

def get_equifax_client() -> EquifaxClient:
    '''EquifaxClient singleton implementation'''
    global _equifax_client_instance

    # If client instance doesn't exist
    if _equifax_client_instance is None:
        login_url = os.getenv("URL_TOKEN")
        request_url = os.getenv("URL_REPORT")
        user_natural = os.getenv("USER_NATURAL")
        password_natural = os.getenv("PASSWORD_NATURAL")
        user_juridica = os.getenv("USER_JURIDICA")
        password_juririca = os.getenv("PASSWORD_JURIDICA")
        token_natural = os.getenv("TOKEN_INTERNO_NATURAL")
        token_juridica = os.getenv("TOKEN_INTERNO_JURIDICA")
        scope = os.getenv("SCOPE")

        # If some parameters are not present, raise exception
        if None in (
            login_url,
            request_url,
            user_natural,
            password_natural,
            user_juridica,
            password_juririca,
            token_natural,
            token_juridica
            ):
            missing = []
            if login_url is None: missing.append("URL_TOKEN")
            if request_url is None: missing.append("URL_REPORT")
            if user_natural is None: missing.append("USER_NATURA")
            if password_natural is None: missing.append("PASSWORD_NATURAL")
            if user_juridica is None: missing.append("USER_JURIDICA")
            if password_juririca is None: missing.append("PASSWORD_JURIDICA")
            if token_natural is None: missing.append("TOKEN_INTERNO_NATURAL")
            if token_juridica is None: missing.append("TOKEN_INTERNO_JURIDICA")
            if scope is None: missing.append("SCOPE")

            raise RuntimeError(
                f"Missing environment variables: {', '.join(missing)}\n"
                "Please check your .env file or environment configuration."
            )
        
        # Create instance
        _equifax_client_instance = EquifaxClient(
            login_url=login_url,
            request_url=request_url,
            user_natural=user_natural,
            password_natural=password_natural,
            user_juridica=user_juridica,
            password_juridca=password_juririca,
            token_natural=token_natural,
            token_juridica=token_juridica,
            scope=scope
        )

    # Return instance
    return _equifax_client_instance




