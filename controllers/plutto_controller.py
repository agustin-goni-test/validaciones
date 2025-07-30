from clients.plutto_client import get_plutto_client
import json
from library.plutto_components import WatchlistResponse
from controllers.output_controller import OutputController
import pandas as pd

class PluttoController:

    def __init__(self, plutto_client):
        self.plutto_client = plutto_client
        self.output_controller = None


    def check_watchlists(self, row: pd.Series, index: int) -> pd.Series:
        """
        Checks the watchlists for a given ID.
        """
        # Get Plutto client instance if not already set
        if not self.plutto_client:
            self.plutto_client = get_plutto_client()

        # Initialize the output controller if not already set
        self.get_output_controller()       

        # Create output data as array
        output_data = []

        id = row['Id']
        rut = row['Rut']

        if not self.output_controller.headers:
            header = [
                "RUT",
                "Número",
                "Nombre",
                "Total Hits",
                "Total Blacklist Hits",
                "Source",
                "Risk Level",
                "Hit",
                "Hit Type",
                "Risk Level",
                "Source",
                "Programa",
                "Remarks"
            ]

            self.output_controller.write_headers(header)

        

        print(f"Revisando refrencias de watchlists en el índice {index} para el RUT {rut} y ID {id}")
        
        # Early skip condition, if already checked, return
        if row.get("PEP") != "S/I" and row.get("Watchlist") != "S/I":
            print(f"Comercio en índice {index} con RUT y ID {id} ya fue validado. Lo omitiremos")
            return None

        # Control for error condition
        if id == "No":
            # This means the original ID report could not be found. Can`t process it
            print(f"El comercio {rut} no tiene ID. No es posible obtener su reporte.")
            return None

        # Obtain watchlist validation from Plutto client
        found, watchlist_json = self.plutto_client.obtain_watchlists(id)
        
        if found:
            watchlist_response = WatchlistResponse(watchlist_json)

            found_pep = self._is_pep(watchlist_response)
            found_person_of_interest = self._is_person_of_interest(watchlist_response)

            watchlist_number = 1

            for watchlist in watchlist_response.watchlists:
                
                output_data.append(rut)
                output_data.append(f"Watchlist #{watchlist_number}")
                output_data.append(f"{watchlist.watchlistable_name}")
                # data_to_write = f"Watchlist #{watchlist_number}"
                # output_data.append(f"Watchlist #{watchlist_number}")

                watchlist_number += 1

                if not watchlist.hits:
                    print(f"No se encontraron hits para el ID: {id}.")
                    return
                else:
                    hits = len(watchlist.hits)

                    # data_to_write += f" : {hits} hits"
                    
                    # output_data.append(f"Watchlist {watchlist_number - 1}: {hits} hits")

                    output_data.append(f"{watchlist.total_hits}")
                    output_data.append(f"{watchlist.total_blacklist_hits}")
                    output_data.append(f"{watchlist.source}")
                    output_data.append(f"{watchlist.risk_level}")
                    
                    # print(f"Se encontraron {hits} hits para el ID: {id}.")
                    # print(f"Parámetro total_hits: {watchlist.total_hits}")
                    # print(f"Parámetro total_blacklist_hits: {watchlist.total_blacklist_hits}")
                    # print(f"Parámetro source: {watchlist.source}")
                    # print(f"Parámetro risk_level: {watchlist.risk_level}")
                    hit_number = 1

                    for hit in watchlist.hits:
                        
                        output_data.append(f"{hit.full_name}")
                        output_data.append(f"{hit.hit_type}")
                        output_data.append(f"{hit.risk_level}")
                        
                        # print(f"\nHit #{hit_number}:")
                        # print(f"Nombre: {hit.full_name}")
                        # print(f"Hit type: {hit.hit_type}")
                        # print(f"Risk level: {hit.risk_level}")
                        hit_number += 1

                        list_match_number = 1

                        # list_matches = len(hit.list_matches)
                        # data_to_write += f" : {list_matches} matches"

                        # output_data.append(data_to_write)

                        if not hit.list_matches:

                            output_data.append("N/A")
                            output_data.append("N/A")
                            output_data.append("N/A")

                        for list_match in hit.list_matches:

                            output_data.append(f"{list_match.source}")
                            output_data.append(f"{list_match.program}")
                            output_data.append(f"{list_match.remarks}")

                            # print(f"\nCoincidencia #{list_match_number}:")
                            list_match_number += 1
                            # print(f"source: {list_match.source}")
                            # print(f"program: {list_match.program}")
                            # print(f"remarks: {list_match.remarks}")

                        self.output_controller.write_output(output_data)
                        
                        # Eliminate all elementos in output_data to start over
                        output_data.clear()

            print(f"\nPEP encontrado: {found_pep}")
            print(f"Persona de interés encontrada: {found_person_of_interest}")
            row['PEP'] = "Sí" if found_pep else "No"
            row['Watchlist'] = "Sí" if found_person_of_interest else "No"

            # output_data.append("\n")
            # self.output_controller.write_output(output_data

            return row
                        
        else:
            print(f"No pudimos obtener información para ID: {id}.")
            return None


    def _is_pep(self, response: WatchlistResponse) -> bool:
        ''' Check if the response contains a PEP hit. '''
        found = False
        
        # Iterate through the watchlists and hits to find PEP matches
        for watchlist in response.watchlists:

            # Iterate through the hits in the watchlist
            for hit in watchlist.hits:
                
                # Iterate through the list matches in the hit
                for match in hit.list_matches:

                    # If "PEP is found
                    if "PEP" in match.category or "PEP" in match.program:
                        found = True
                        break
                        
        return found

    def _is_person_of_interest(self, response: WatchlistResponse) -> bool:
        ''' Check if the response contains a person of interest hit. '''
        found = False
        
        # Iterate through the watchlists and hits to find person of interest matches
        for watchlist in response.watchlists:

            # If at least one black list hit is found
            if watchlist.total_blacklist_hits > 0:
                found = True
                break
                        
        return found
    

    def get_output_controller(self) -> None:
        """
        Returns the OutputController instance.
        """
        if self.output_controller is None:
            self.output_controller = OutputController(excel_file="output.xlsx")
            self.output_controller.select_output_format(
                csv_enabled=False,
                excel_enabled=True,
                txt_enabled=False
                )
        

