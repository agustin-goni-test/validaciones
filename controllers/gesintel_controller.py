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
            self.output_controller = OutputController(excel_file="GESINTEL_output.xlsx")
            self.output_controller.select_output_format(
                csv_enabled=False,
                excel_enabled=True,
                txt_enabled=False
                )
            

    def check_watchlists(self, row: pd.Series, index: int) -> pd.Series:

        if self.gesintel_client is None:
            self.gesintel_client = get_gestintel_client()

        self.get_output_controller()

        rut_original = str(row['Rut'])
        rut = rut_original.replace("-", "")

        try:
            found, json = self.gesintel_client.get_aml_result(rut)

            if found:
                # print(f"Reporte encontrado para RUT {rut}. Convirtiendo a objeto...")
                report = AMLResultResponse.model_validate(json)
                # print(f"Status = {report.status}")
                
                if report.results.negativeResults:
                    print(f"Índice {index},  RUT {rut} TIENE RESULTADOS NEGATIVOS!!!!!")
                    for result in report.results.negativeResults:
                        print(result)

                else:
                    print(f"Índice {index}, RUT {rut} no tiene resultados negativos...")

        except Exception as e:
            print(f"Error processing RUT {rut}: {e}")
        
        
            

    