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

        if self.gesintel_client is None:
            self.gesintel_client = get_gestintel_client()

        self.get_output_controller()

        rut_original = str(row['Rut'])
        rut = rut_original.replace("-", "")

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

        if row['PEP Ges'] != "S/I":
            print(f"Comercio en índice {index} con RUT y ID {id} ya fue validado. Lo omitiremos")
            return None

        hit_data = [rut_original, "No", "No", "No", "No", "No", "No","No", "No", "No", "No", "No"]

        found_hits = []

        try:
            found, json = self.gesintel_client.get_aml_result(rut)

            if found:
                # print(f"Reporte encontrado para RUT {rut}. Convirtiendo a objeto...")
                report = AMLResultResponse.model_validate(json)

                if report.results.pepCResults:
                    hit_data[1] = "Si"
                    found_hits.append("PEP")

                if report.results.pepHResults:
                    hit_data[2] = "Si"
                    found_hits.append("PEP Histórico")

                if report.results.pepCResults:
                    hit_data[3] = "Si"
                    found_hits.append("PEP Candidato")

                if report.results.fpResults:
                    hit_data[4] = "Si"
                    found_hits.append("fp")

                if report.results.pjudResults:
                    hit_data[5] = "Si"
                    found_hits.append("Poder judicial")

                if report.results.personResults:
                    hit_data[6] = "Si"
                    found_hits.append("PEP")

                if report.results.djResults:
                    hit_data[7] = "Si"
                    found_hits.append("dj")

                if report.results.negativeResults:
                    hit_data[8] = "Si"
                    found_hits.append("Negative")

                if report.results.vipResults:
                    hit_data[9] = "Si"
                    found_hits.append("VIP")
                    
                if report.results.pepRelacionados:
                    hit_data[10] = "Si"
                    found_hits.append("PEP Relacionado")

                if report.results.pepHRelacionados:
                    hit_data[11] = "Si"
                    found_hits.append("PEP Histórico Rel")
                
                
                self.output_controller.write_output(hit_data)
                
                if found_hits:
                    print(f"Índice {index}, RUT {rut_original} --- ENCONTRADO")
                    row['PEP Ges'] = "Si"

                else:
                    print(f"Índice {index}, RUT {rut_original} --- no encontrado...")
                    row['PEP Ges'] = "No"

                return row


        except Exception as e:
            print(f"Error processing RUT {rut}: {e}")
            return None
        
        
            

    