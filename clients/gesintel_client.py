from typing import Optional
import os
import requests

class GestintelClient:
    def __init__(
        self,
        gesintel_url: str,
        api_key: str,
        endpoint_getaml_result: str,
        endpoint_getaml_risk: str,
        endpoint_get_flag_results: str,
        endpoint_getaml_report: str,
        endpoint_get_entity_data: str,
        endpoint_get_entity_record: str,
        debug: bool
    ):
        self.gesintel_url = gesintel_url
        self.api_key = api_key
        self.endpoint_getaml_result = endpoint_getaml_result
        self.endpoint_getaml_risk = endpoint_getaml_risk
        self.endpoint_get_flag_results = endpoint_get_flag_results
        self.endpoint_getaml_report = endpoint_getaml_report
        self.endpoint_get_entity_data = endpoint_get_entity_data
        self.endpoint_get_entity_record = endpoint_get_entity_record
        self.debug = True if debug == "true" else False


    def get_aml_result(self, rut: str) -> tuple[bool, str]:
        '''
        Implements GET on getAMLResult through the generic request (internal method)
        '''
        
        url = self.gesintel_url + self.endpoint_getaml_result

        if self.debug:
            print(f"Method getAMLResult, URL: {url}")

        return self._perform_get_request(url, rut)
    

    def get_aml_risk(self, rut: str) -> tuple[bool, str]:
        '''
        Implements GET on getAMLRisk through the generic request (internal method).
        '''
        
        url = self.gesintel_url + self.endpoint_getaml_risk

        if self.debug:
            print(f"Method getAMLRisk, URL: {url}")

        return self._perform_get_request(url, rut)
    

    def get_aml_report(self, rut: str) -> tuple[bool, str]:
        '''
        Implements GET on getAMLReport through the generic request.
        '''

        url = self.gesintel_url + self.endpoint_getaml_report

        if self.debug:
            print(f"Method getAMLReport, URL: {url}")

        return self._perform_get_request(url, rut)
    

    def get_flag_results(self, rut: str) -> tuple[bool, str]:
        '''
        Implements GET on getFlagResults through the generic request.
        '''

        url = self.gesintel_url + self.endpoint_get_flag_results

        if self.debug:
            print(f"Method getFlagResults, URL: {url}")

        return self._perform_get_request(url, rut)


    def get_entity_data(self, rut: str) -> tuple[bool, str]:
        '''
        Implements GET on getEntityData through the generic request.
        '''

        url = self.gesintel_url + self.endpoint_get_entity_data

        if self.debug:
            print(f"Method getEntityData, URL: {url}")

        return self._perform_get_request(url, rut)
    

    def get_entity_record(self, rut: str) -> tuple[bool, str]:
        '''
        Implements GET on getEntityReport through the generic request.
        '''

        url = self.gesintel_url + self.endpoint_get_entity_record + f"/{rut}"

        if self.debug:
            print(f"Method getEntityReport, URL: {url}")

        # Add headers
        headers = {
            'authorization': f'{self.api_key}'
        }

        # Call service
        response = requests.get(url=url, headers=headers)

        # Control for not found and return False and nothing
        if response.status_code == 404:
            print(f"Informe para RUT {rut} no encontrado...")
            return False, None
        
        # Raise for status
        response.raise_for_status()

        # Return found and the report
        return True, response.json()




    def _perform_get_request(self, url: str, rut: str) -> tuple[bool, str]:
        '''
        Implements a generic GET on the API endpoints. Should work for all of them.

        Raises:
        requests.HTTPError: If the request fails with a non-404 HTTP error.
    
        Returns:
            (bool, dict): Tuple indicating whether the record was found and the JSON response.
                        Returns (False, None) if record not found (404).
        '''

        # Add headers
        headers = {
            'authorization': f'{self.api_key}'
        }

        # Add params
        params = {
            'rut': f'{rut}'
        }

        # Call service
        response = requests.get(url=url, params=params, headers=headers)

        # Control for not found and return False and nothing
        if response.status_code == 404:
            print(f"Informe para RUT {rut} no encontrado...")
            return False, None
        
        # Raise for status
        response.raise_for_status()

        # Return found and the report
        return True, response.json()


 

# Instance of the client
_gesintel_client: Optional[GestintelClient] = None

def get_gestintel_client() -> GestintelClient:
    '''Singleton implementation'''

    global _gesintel_client

    if _gesintel_client is None:
        base_url = os.getenv("BASE_URL_GESINTEL")
        api_key = os.getenv("GESINTEL_API_KEY")
        endpoint_getaml_result = os.getenv("ENDPOINT_GETAML_RESULT")
        endpoint_getaml_risk = os.getenv("ENDPOINT_GETAML_RISK")
        endpoint_getaml_report = os.getenv("ENDPOINT_GETAML_REPORT")
        endpoint_get_flag_results = os.getenv("ENDPOINT_GET_FLAG_RESULTS")
        endpoint_get_entity_data = os.getenv("ENDPOINT_ENTITY_DATA")
        endpoint_get_entity_record = os.getenv("ENDPOINT_ENTITY_RECORD")
        debug = os.getenv("DEBUG")

        if None in (
            base_url,
            api_key,
            endpoint_getaml_result,
            endpoint_getaml_risk,
            endpoint_getaml_report,
            endpoint_get_flag_results,
            endpoint_get_entity_data,
            endpoint_get_entity_record
        ):
        
            missing = []

            if base_url is None: missing.append("BASE_URL_GESINTEL")
            if api_key is None: missing.append("GESINTEL_API_KEY")
            if endpoint_getaml_result is None: missing.append("ENDPOINT_GETAML_RESULT")
            if endpoint_getaml_risk is None: missing.append("ENDPOINT_GETAML_RISK")
            if endpoint_getaml_report is None: missing.append("ENDPOINT_GETAML_REPORT")
            if endpoint_get_flag_results is None: missing.append("ENDPOINT_GET_FLAG_RESULTS")
            if endpoint_get_entity_data is None: missing.append("ENDPOINT_ENTITY_DATA")
            if endpoint_get_entity_record is None: missing.append("ENDPOINT_ENTITY_RECORD")

            raise RuntimeError(
                    f"Missing environment variables: {', '.join(missing)}\n"
                    "Please check your .env file or environment configuration."
                )
        
        _gesintel_client = GestintelClient(
            gesintel_url=base_url,
            api_key=api_key,
            endpoint_getaml_result=endpoint_getaml_result,
            endpoint_getaml_risk=endpoint_getaml_risk,
            endpoint_getaml_report=endpoint_getaml_report,
            endpoint_get_flag_results=endpoint_get_flag_results,
            endpoint_get_entity_data=endpoint_get_entity_data,
            endpoint_get_entity_record=endpoint_get_entity_record,
            debug=debug 
        )
    
    return _gesintel_client

