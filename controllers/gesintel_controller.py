from controllers.output_controller import OutputController
import pandas as pd
from clients.gesintel_client import get_gestintel_client
from library.gesintel_components import AMLResultResponse

class GesintelController:
    def __init__(self, gesintel_client):
        self.gesintel_client = gesintel_client
        self.output_controller = None

    def get_output_controller(self) -> None:
        """
        Returns the OutputController instance.
        """
        if self.output_controller is None:
            self.output_controller = OutputController(csv_file="GESINTEL_output.csv")
            self.output_controller.select_output_format(
                csv_enabled=True,
                excel_enabled=False,
                txt_enabled=False
                )
            

    def check_watchlists(self, row: pd.Series, index: int) -> pd.Series:

        # Get the client if it's not yect created
        if self.gesintel_client is None:
            self.gesintel_client = get_gestintel_client()

        # Create the output controller to handle the writing to file
        self.get_output_controller()

        # Get the RUT, both the original and modified version
        rut_original = str(row['Rut'])
        rut = rut_original.replace("-", "")

        # Add headers to the output file if needed
        if not self.output_controller.headers:
            header = [
                "RUT",
                "PEP",
                "PEP Histórico",
                "PEP Candidato",
                "fpResults",
                "PJUD",
                "Persona",
                "djResults",
                "Negativo",
                "VIP",
                "PEPRelacionado",
                "PEP Hist Relacionado"
            ]

            self.output_controller.write_headers(header)

        
        # Check if the row is already processed
        if row['PEP Ges'] != "S/I" and row['Watch Ges'] != "S/I" and row['PJ Ges'] != "S/I":
            print(f"Comercio en índice {index} con RUT y ID {id} ya fue validado. Lo omitiremos")
            return None

        # List all the potential hits (for later dumping into the output file)
        hit_data = [rut_original, "No", "No", "No", "No", "No", "No","No", "No", "No", "No", "No"]

        # Collect hits and conditions
        found_hits = []
        found_pep = False
        found_watchlist = False
        found_pj = False

        try:
            # Get the report
            found, json = self.gesintel_client.get_aml_result(rut)

            if found:
                # print(f"Reporte encontrado para RUT {rut}. Convirtiendo a objeto...")
                # Convert to object
                report = AMLResultResponse.model_validate(json)

                # Check each of the results. There might be multiple hits.
                # Determine if PEP related or watchlist related
                if report.results.pepCResults:
                    hit_data[1] = "Si"
                    found_hits.append("PEP")
                    found_pep = True

                if report.results.pepHResults:
                    hit_data[2] = "Si"
                    found_hits.append("PEP Histórico")
                    found_pep = True

                if report.results.pepCResults:
                    hit_data[3] = "Si"
                    found_hits.append("PEP Candidato")
                    found_pep = True

                if report.results.fpResults:
                    hit_data[4] = "Si"
                    found_hits.append("fp")
                    found_pep = True

                if report.results.pjudResults:
                    hit_data[5] = "Si"
                    found_hits.append("Poder judicial")
                    # found_watchlist = True
                    found_pj = True

                if report.results.personResults:
                    hit_data[6] = "Si"
                    found_hits.append("PEP")
                    found_watchlist = True

                # if (report.results.djResults and 
                #     report.results.djResults.wlResults and 
                #     len(report.results.djResults.wlResults) > 0):
                #     hit_data[7] = "Si"
                #     found_hits.append("dj")
                #     found_pep = True

                # This is the logic that will capture watchlist hits
                if report.results and report.results.djResults:
                    dj_results = report.results.djResults
                    
                    # Check if wlResults exists and has content (WATCHLIST)
                    wl_exists = ('wlResults' in dj_results and 
                                dj_results['wlResults'] is not None and 
                                len(dj_results['wlResults']) > 0)
                    
                    # Check if ameResults exists and has content (WATCHLIST)
                    ame_exists = ('ameResults' in dj_results and 
                                dj_results['ameResults'] is not None and 
                                len(dj_results['ameResults']) > 0)
                    
                    # Check if socResults exists and has content (PEP)
                    soc_exists = ('socResults' in dj_results and 
                                dj_results['socResults'] is not None and 
                                len(dj_results['socResults']) > 0)
                    
                    # Set flags based on conditions
                    if wl_exists or ame_exists:
                        found_watchlist = True # Found watchlist hit
                        hit_data[7] = "Si"  # Assuming this is for watchlist hits
                        found_hits.append("dj")
                    
                    if soc_exists:
                        hit_data[7] = "Si"
                        found_pep = True # Found state owned conpany, is PEP
                        found_hits.append("dj")

                if report.results.negativeResults:
                    hit_data[8] = "Si"
                    found_hits.append("Negative")
                    found_watchlist = True

                if report.results.vipResults:
                    hit_data[9] = "Si"
                    found_hits.append("VIP")
                    found_pep = True
                    
                if report.results.pepRelacionados:
                    hit_data[10] = "Si"
                    found_hits.append("PEP Relacionado")
                    found_pep = True

                if report.results.pepHRelacionados:
                    hit_data[11] = "Si"
                    found_hits.append("PEP Histórico Rel")
                    found_pep = True
                
                
                self.output_controller.write_output(hit_data)
                
                # If any hits were found, notate them in row,
                # according to PEP or watchlist (or both)
                if found_hits:
                    print(f"Índice {index}, RUT {rut_original} --- ENCONTRADO, escribiendo en archivo de salida")
                    row['PEP Ges'] = "Si" if found_pep else "No"
                    row['Watch Ges'] = "Si" if found_watchlist else "No"
                    row['PJ Ges'] = "Si" if found_pj else "No"
                
                # If not, declare not found in row
                else:
                    print(f"Índice {index}, RUT {rut_original} --- no encontrado... escribiendo en archivo de salida")
                    row['PEP Ges'] = "No"
                    row['Watch Ges'] = "No"
                    row['PJ Ges'] = "No"

                return row


        except Exception as e:
            print(f"Error processing RUT {rut}: {e}")
            return None
        
        
            

    