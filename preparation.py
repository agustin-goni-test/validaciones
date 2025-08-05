import pandas as pd
import os
import tempfile
import shutil
from clients.plutto_client import get_plutto_client
from clients.gesintel_client import get_gestintel_client
import time
from controllers.plutto_controller import PluttoController
from controllers.gesintel_controller import GesintelController


class ValidationControlFlow:
    def __init__(self, excel_file: str):
        """
        Initializes the class with the given Excel file path.
        Loads the content into a pandas DataFrame.
        """
        self.filename = excel_file

        try:
            self.df = pd.read_excel(excel_file)
            print(f"Loaded Excel file: {excel_file} with {len(self.df)} rows.")

        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file '{excel_file}' not found.")
        except Exception as e:
            raise RuntimeError(f"Failed to load Excel file '{excel_file}': {str(e)}")
        
    
    def prepare_data(self) -> bool:
        """
        Prepares the data in the DataFrame.
        This method is used to get all the Plutto report for each customer.
        More specifically, it will check if they are available. If not, it will
        request them.
        """
        # Example preparation: Check if DataFrame is empty
        if self.df.empty:
            print("Archivo vacío. No hay datos para trabajar")
            return False
        
        # Validate the required columns
        self._validate_preparation_columns()

        # Run the preparation process by block of rows, from 0 to the size of the DataFrame
        # Use a set block size to avoid memory issues
        block_size = 100
        for start in range(0, len(self.df), block_size):

            end = min(start + block_size, len(self.df))
            block = self.df.iloc[start:end]


            print(f"Procesando filas {start} a {end - 1}...") 

            self._prepare_block(block)

            self.save_to_excel()
            # input("Continuar con el siguiente bloque...")

            time.sleep(5)

            # input("Presione Enter para continuar con el siguiente bloque...")

        
    def _validate_preparation_columns(self) -> None:

        if 'Rut' not in self.df.columns:
            raise ValueError("La columna 'Rut' no existe en el DataFrame.")

        required_columns = ['Existe informe', 'Informe solicitado', "Id"]

        for col in required_columns:
            if col not in self.df.columns:
                self.df[col] = "No"
                print("Columna agregada:", col)

    
    def _validate_watchlist_columns(self) -> None:
        required_columns = ['PEP', 'Watchlist']

        for col in required_columns:
            if col not in self.df.columns:
                self.df[col] = "S/I"
                print("Columna agregada:", col)


    def _prepare_block(self, block: pd.DataFrame) -> None:

        plutto_client = get_plutto_client()

        # Take each row from the block
        for index, row in block.iterrows():
            rut = row['Rut']
            print(f"Procesando RUT: {rut} en índice {index}")

            # Check if the report already existed, or if it has been requested.
            # Only use the services if it hasn't been requested yet.
            if row['Id'] == "No":

                # Here you would call the Plutto client to get the report
                found, report = plutto_client.obtain_validation_by_tin(rut)
                
                # If report was found
                if found:
                    self.df.at[index, 'Existe informe'] = "Sí"
                    id = report.get('entity_validation', {}).get('id', "No")
                    self.df.at[index, 'Id'] = id if id else "No"
                    print(f"Informe para el RUT {rut}, con id {id} ya estaba disponible.")

                # Else (report not found, 404, must create it)
                else:
                    print(f"Informe no exitía. Solicitando informe para el RUT {rut}")
                    
                    # Create report
                    created, id = plutto_client.obtain_validation(rut)
                    
                    # If creation worked
                    if created:
                        # Report requestes (not existing)
                        self.df.at[index, 'Informe solicitado'] = "Sí"
                        # Report will be available
                        self.df.at[index, 'Id'] = id if id else "No"
                        print(f"Informe solicitado exitosamente, id de comercio: {id}.")
                    
                    # If it didn't work
                    else:
                        # Report not requested (request failed) and hence not available
                        self.df.at[index, 'Informe solicitado'] = "No"
                        self.df.at[index, 'Id'] = "No"
                        print("No se pudo solicitar el informe.")

            else:  
                print(f"El informe para el RUT {rut} ya estaba disponible.")
                            
            
    def validate_availability(self) -> bool:
        '''Validate if all reports are already available.
        If not, returns False'''
        
        # Check if columns "Disponible" exists in DataFrame
        if 'Disponible' not in self.df.columns:
            print(f"Columna 'Disponible' no encontrada en el archivo. Es necesario preparar los datos primero.")
            return False
        
        # else:


    def save_to_excel(self) -> None:
        """
        Saves the current DataFrame back to the original Excel file path.
        If the file is open or locked, it writes to a temp file and replaces it.
        """
        try:
            # Write to a temp file first to avoid issues if the original is open
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                temp_path = tmp.name
                self.df.to_excel(temp_path, index=False, engine='openpyxl')

            # Overwrite the original file
            shutil.move(temp_path, self.filename)
            print(f"Saved DataFrame to {self.filename}")
        except Exception as e:
            raise RuntimeError(f"Failed to save Excel file '{self.filename}': {str(e)}")


    def run_watchilist_workflow(self) -> bool:
        """
        Runs the workflow to check watchlists for each RUT in the DataFrame.
        """

        # Get Plutto client instance
        plutto_client = get_plutto_client()

        # Initialize the controller
        controller = PluttoController(plutto_client)

        self._validate_watchlist_columns()

        # Process by block
        block_size = 50
        
        for start in range(0, len(self.df), block_size):
            end = min(start + block_size, len(self.df))
            block = self.df.iloc[start:end]

            print(f"Procesando filas {start} a {end - 1}...") 

            # Iterate through each row in the block
            for index, row in block.iterrows():
                id = row['Id']
                print(f"Revisando watchlists para el ID: {id}")

                # Call the controller to check watchlists
                updated_row = controller.check_watchlists(row, index)

                if updated_row is not None:
                    self.df.loc[index] = updated_row

                # time.sleep(3)
                # input("\n\nContinuar con el siguiente ID...")

            # Save the DataFrame block back to the Excel file
            self.save_to_excel()
            time.sleep(5)
        
        # # Iterate through each row in the DataFrame, by blocks
        # for index, row in self.df.iterrows():
        #     id = row['Id']
        #     print(f"Revisando watchlists para el ID: {id}")

        #     # Call the controller to check watchlists
        #     controller.check_watchlists(row, index)

        #     input("\n\nContinuar con el siguiente ID...")

    
    def run_gesintel_watchlist_workflow(self, block_size: int = 10):
        
        gesintel_client = get_gestintel_client()
        
        controller = GesintelController(gesintel_client)
        total_rows = len(self.df)

        # Process by block
        block_size = 10

        for start in range(0, total_rows, block_size):
            end = min(start + block_size, total_rows)
            block = self.df.iloc[start:end]

            print(f"Procesando filas {start} to {end - 1}")

            for index, row in block.iterrows():
                rut = row['Rut']
                # print(f"Vamos a procesar comercio {rut}...")
                
                controller.check_watchlists(row, index)

            # input("Continuar...")


