from clients.plutto_client import get_plutto_client
import json
from library.plutto_components import WatchlistResponse
import pandas as pd

class PluttoController:

    def __init__(self, plutto_client):
        self.plutto_client = plutto_client


    def check_watchlists(self, row: pd.Series, index: int) -> pd.Series:
        """
        Checks the watchlists for a given ID.
        """
        # Get Plutto client instance if not already set
        if not self.plutto_client:
            self.plutto_client = get_plutto_client()

        id = row['Id']
        rut = row['Rut']

        print(f"Revisando refrencias de watchlists en el índice {index} para el RUT {rut} y ID {id}")
        
        # Early skip condition, if already checked, return
        if row.get("PEP") != "S/I" and row.get("Watchlist") != "S/I":
            print(f"Comercio en índice {index} con RUT y ID {id} ya fue validado. Lo omitiremos")
            return None

        # Obtain watchlist validation from Plutto client
        found, watchlist_json = self.plutto_client.obtain_watchlists(id)
        
        if found:
            watchlist_response = WatchlistResponse(watchlist_json)

            found_pep = self._is_pep(watchlist_response)
            found_person_of_interest = self._is_person_of_interest(watchlist_response)

            watchlist_number = 1
            for watchlist in watchlist_response.watchlists:
                print(f"\nWatchlist #{watchlist_number}:")
                watchlist_number += 1
                print(f"Watchlist obtenida con éxito para {watchlist.watchlistable_name}.")
                if not watchlist.hits:
                    print(f"No se encontraron hits para el ID: {id}.")
                    return
                else:
                    hits = len(watchlist.hits)
                    print(f"Se encontraron {hits} hits para el ID: {id}.")
                    print(f"Parámetro total_hits: {watchlist.total_hits}")
                    print(f"Parámetro total_blacklist_hits: {watchlist.total_blacklist_hits}")
                    print(f"Parámetro source: {watchlist.source}")
                    print(f"Parámetro risk_level: {watchlist.risk_level}")
                    hit_number = 1

                    for hit in watchlist.hits:
                        print(f"\nHit #{hit_number}:")
                        print(f"Nombre: {hit.full_name}")
                        print(f"Hit type: {hit.hit_type}")
                        print(f"Risk level: {hit.risk_level}")
                        hit_number += 1

                        list_match_number = 1

                        if not hit.list_matches:
                            print("No se encontraron coincidencias en las listas para este hit.")

                        for list_match in hit.list_matches:
                            print(f"\nCoincidencia #{list_match_number}:")
                            list_match_number += 1
                            print(f"source: {list_match.source}")
                            print(f"program: {list_match.program}")
                            print(f"remarks: {list_match.remarks}")

            print(f"\nPEP encontrado: {found_pep}")
            print(f"Persona de interés encontrada: {found_person_of_interest}")
            row['PEP'] = "Sí" if found_pep else "No"
            row['Watchlist'] = "Sí" if found_person_of_interest else "No"
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
    
