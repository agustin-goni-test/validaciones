import pandas as pd
import os
import tempfile
import shutil
from clients.plutto_client import get_plutto_client

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
        self._validate_prepation_columns()

        # Run the preparation process by block of rows, from 0 to the size of the DataFrame
        # Use a set block size to avoid memory issues
        block_size = 10
        for start in range(0, len(self.df), block_size):

            end = min(start + block_size, len(self.df))
            block = self.df.iloc[start:end]


            print(f"Processing rows {start} to {end - 1}...") 

            self._prepare_block(block)

            self.save_to_excel()
            input("Continue to the next block...")

            

        
    def _validate_prepation_columns(self) -> None:

        if 'Rut' not in self.df.columns:
            raise ValueError("La columna 'Rut' no existe en el DataFrame.")

        required_columns = ['Existe informe', 'Informe solicitado']

        for col in required_columns:
            if col not in self.df.columns:
                self.df[col] = "No"
                print("Columna agregada:", col)


    def _prepare_block(self, block: pd.DataFrame) -> None:

        plutto_client = get_plutto_client()

        # Take each row from the block
        for index, row in block.iterrows():
            rut = row['Rut']
            print(f"Procesando RUT: {rut} en índice {index}")

            # Check if the report already existed, or if it has been requested.
            # Only use the services if it hasn't been requested yet.
            if row['Existe informe'] == "No" and row['Informe solicitado'] == "No":

                # Here you would call the Plutto client to get the report
                found, report = plutto_client.obtain_validation_by_tin(rut)
                self.df.at[index, 'Existe informe'] = "Sí" if found else "No"

                if not found:
                    print(f"Informe no exitía. Solicitando informe para el RUT {rut}")
                    created = plutto_client.obtain_validation(rut)
                    if created:
                        self.df.at[index, 'Informe solicitado'] = "Sí"
                        self.df.at[index, 'Existe informe'] = "Sí"
                        print("Informe solicitado exitosamente.")
                    else:
                        self.df.at[index, 'Informe solicitado'] = "No"
                        print("No se pudo solicitar el informe.")

                else:
                    print(f"Informe ya existía para el RUT {rut}.")

            else:  
                print(f"El informe para el RUT {rut} ya existe o ha sido solicitado previamente.")
                self.df.at[index, 'Informe solicitado'] = "Si"
                self.df.at[index, 'Existe informe'] = "Si"
            
   
        



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



