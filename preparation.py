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

            # Check if elimination of duplicates is needed
            self._eliminate_duplicates()

        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file '{excel_file}' not found.")
        except Exception as e:
            raise RuntimeError(f"Failed to load Excel file '{excel_file}': {str(e)}")
        
    
    def _eliminate_duplicates(self) -> None:
        '''
        Eliminates duplicate RUTs from the file.
        First, it checks if duplicates exist.
        '''

        # Check if RUTs are duplicated
        if self.df['Rut'].duplicated().any():
            initial_count = len(self.df)

            # Remove duplicates and update
            self.df = self.df.drop_duplicates(subset=['Rut'], keep="first")
            final_count = len(self.df)
            print(f"Removed {initial_count - final_count} duplicated RUTs.")

            # Save to Excel to process this file
            self.df.to_excel(self.filename, index=False)
            print(f"Updated file to: {self.filename}")
        
        else:
            print("No duplicates RUTs found.")
        
    
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
        '''This method checks if the control columns needed for Plutto validations
        are part of the original Excel file. If they don't exist, the method
        creates them with a default value for each row'''
        
        # List the required columns
        required_columns = ['PEP', 'Watchlist']

        # For each required column, if they don't exist, create them
        for col in required_columns:
            if col not in self.df.columns:
                self.df[col] = "S/I"
                print("Columna agregada:", col)


    def _validate_gestintel_watchlist_columns(self) -> None:
        '''This method checks if the control columns needed for Gesintel validations
        are part of the original Excel file. If they don't exist, the method
        creates them with a default value for each row'''

        # List the required columns
        required_columns = ['PEP Ges', 'Watch Ges', "PJ Ges"]

        # For each required column, if they don't exist, create them
        for col in required_columns:
            if col not in self.df.columns:
                self.df[col] = "S/I"
                print("Columna agregada:", col)


    def _prepare_block(self, block: pd.DataFrame) -> None:
        '''Prepares the commerce list for use with Plutto.
        This is required because we want to make sure the complete Plutto report
        exists in the service. If it's not there, we will request its creation.'''

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



    def run_stats(self) -> None:
        '''
        Run a statistics workflow for Plutto.
        '''
        if self.df.empty:
            print("Archivo vacío. No hay datos para trabajar")
            return False
        
        self.output_file = "plutto_stats_output.xlsx"

        EXCEL_COLUMNS = [
            "RUT",
            "Actividades",
            "País",
            "Tipo_compañia",
            "Fecha_constitución",
            "Gerentes",
            "Representantes",
            "Accionistas",
            "Total_participación",
            "Fuente"
        ]

        pd.DataFrame(columns=EXCEL_COLUMNS).to_excel(
            self.output_file,
            index=False,
            engine='openpyxl')
        
        block_size = 10
        
        for start in range(0, len(self.df), block_size):
            end = min(start + block_size, len(self.df))
            block = self.df.iloc[start:end]

            print(f"Procesando filas {start} a {end - 1}...") 

            self._obtain_stats_block(block)

            # input("Continuar con el siguiente bloque...")

            time.sleep(1)


    def check_completeness(self) -> None:
        '''
        Check if the data is present
        '''

        self.output_file = "plutto_stats_output.xlsx"

        try:
            df = pd.read_excel(self.output_file)
        except FileNotFoundError:
            raise RuntimeError(
                f"Output file not found: {self.output_path}. "
                "Run run_stats() first."
            )
        
        
        df_valid = df[df["RUT"].notna()]

        # Filter to only consider the required IDs.
        df_valid = df_valid[df_valid["Fuente"] != "Persona natural"]
        # df_valid = df_valid[df_valid["Fuente"] != "Registro Electrónico"]

        total_rows = len(df_valid)

        # Rule 1: at least 1 activity
        rule_activities = df_valid['Actividades'].fillna(0) >= 1
        success_rate_activities = round(
            (rule_activities.sum() / total_rows) * 100 , 2)

        # Rule 2: País cannot be null or N/A
        rule_country  = df_valid['País'].notna() & (df_valid['País'] != "N/A")
        success_rate_country = round(
            (rule_country.sum() / total_rows) * 100 , 2)

        # Rule 3: Tipo_compañia cannot be null or N/A
        rule_type = df_valid['Tipo_compañia'].notna() & (df_valid['Tipo_compañia'] != "N/A")
        success_rate_company_type = round(
            (rule_type.sum() / total_rows) * 100 , 2)
        
        # Rule 4: Fecha_constitución cannot be null or N/A
        rule_formation_date = df_valid['Fecha_constitución'].notna() & (df_valid['Fecha_constitución'] != "N/A")
        success_rate_date = round(
            (rule_formation_date.sum() / total_rows) * 100 , 2)
        
        # Rule 5: Managers must be at least 1
        rule_managers = df_valid['Gerentes'].fillna(0) >= 1
        success_rate_managers = round(
            (rule_managers.sum() / total_rows) * 100 , 2)

        # Rule 6: Representatives must be at least 1
        rule_representatives = df_valid['Representantes'].fillna(0) >= 1
        success_rate_representatives = round(
            (rule_representatives.sum() / total_rows) * 100 , 2)

        # Rule 7: Shareholders must be at least 1
        rule_shareholders = df_valid['Accionistas'].fillna(0) >= 1
        success_rate_shareholders = round(
            (rule_shareholders.sum() / total_rows) * 100 , 2)

        # Rule 8: Total participation must be exactly 100%
        rule_participation = df_valid['Total_participación'].fillna(0) == 100.0
        success_rate_participation = round(
            (rule_participation.sum() / total_rows) * 100 , 2)

        # Check percentage of cases belonging to electronic registry
        rule_registry = df_valid["Fuente"] == "Registro Electrónico"
        percentage_electronic_registry = round(
            (rule_registry.sum() / total_rows) * 100, 2) 
        
        # All rules combined
        all_rules = (
            rule_activities &
            rule_country &
            rule_type &
            rule_formation_date &
            rule_managers &
            rule_representatives &
            rule_shareholders &
            rule_participation
            )
        
        overall_success_rate = round(
            (all_rules.sum() / total_rows) * 100 , 2)

        print(f"\n\nTotal de filas: {total_rows}")
        print(f"Porcentaje de filas con al menos 1 actividad: {success_rate_activities}%")
        print(f"Porcentaje de filas con país válido: {success_rate_country}%")
        print(f"Porcentaje de filas con tipo de compañía válido: {success_rate_company_type}%")
        print(f"Porcentaje de filas con fecha de constitución válida: {success_rate_date}%")
        print(f"Porcentaje de filas con al menos 1 gerente: {success_rate_managers}%")
        print(f"Porcentaje de filas con al menos 1 representante: {success_rate_representatives}%")
        print(f"Porcentaje de filas con al menos 1 accionista: {success_rate_shareholders}%")
        print(f"Porcentaje de filas con participación total del 100%: {success_rate_participation}%")
        print(f"Porcentaje de filas que cumplen todas las reglas: {overall_success_rate}%")
        print(f"Porcentaje de filas declaradas en registro electrónico: {percentage_electronic_registry}")

        summary_df = pd.DataFrame([
            {"Regla": "Al menos 1 actividad", "Porcentaje": success_rate_activities},
            {"Regla": "País válido", "Porcentaje": success_rate_country},
            {"Regla": "Tipo de compañía válido", "Porcentaje": success_rate_company_type},
            {"Regla": "Fecha de constitución válida", "Porcentaje": success_rate_date},
            {"Regla": "Al menos 1 gerente", "Porcentaje": success_rate_managers},
            {"Regla": "Al menos 1 representante", "Porcentaje": success_rate_representatives},
            {"Regla": "Al menos 1 accionista", "Porcentaje": success_rate_shareholders},
            {"Regla": "Participación total = 100%", "Porcentaje": success_rate_participation},
            {"Regla": "TODAS las reglas", "Porcentaje": overall_success_rate},
            {"Regla": "Datos obtenidos de registro electrónico", "Porcentaje": percentage_electronic_registry}
        ])

        with pd.ExcelWriter(
            self.output_file,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='replace'
            ) as writer:
            summary_df.to_excel(
                writer,
                index=False,
                sheet_name='Resumen'
            )

    


        # # Check if columns "Disponible" exists in DataFrame
        # if 'Disponible' not in self.df.columns:
        #     print(f"Columna 'Disponible' no encontrada en el archivo. Es necesario preparar los datos primero.")
        #     return False
        
        # # else:

    
    def _append_stats_to_output(self, row: dict) -> None:
        '''
        Appends a single row of stats to the output Excel file.
        '''
        df_row = pd.DataFrame([row])

        with pd.ExcelWriter(
            self.output_file,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='overlay'
            ) as writer:
            sheet = writer.sheets['Sheet1']
            startrow = sheet.max_row

            df_row.to_excel(
                writer,
                index=False,
                header=False,
                startrow=startrow
            )



    def _obtain_stats_block(self, block: pd.DataFrame) -> None:
        '''
        Get Plutto report to compile stats about the commerce.
        '''

        plutto_client = get_plutto_client()

        # Take each row from the block
        for index, row in block.iterrows():
            rut = row['Rut']
            print(f"Procesando RUT: {rut} en índice {index}")

            # Here you would call the Plutto client to get the report
            found, report = plutto_client.obtain_validation_by_tin(rut)
            
            # If report was found
            if found:
                    # Obtain entity section
                    entity = (
                        report
                        .get("entity_validation", {})
                        .get("last_validation", {})
                        .get("entity", {})
                    )

                    # Obtain other subsections needed for stats
                    tax_data = entity.get("tax_office_data", {})
                    formation = entity.get("formation", {})
                    administration = formation.get("administration", {})
                    equity = formation.get("equity", {})
                    category = entity.get("category", {})
                    
                    # Obtain activities and their count
                    if tax_data is None:
                        activities = []
                    else:
                        activities = tax_data.get("activities", [])
                    num_activities = len(activities)

                    # Obtain formations stats
                    formation_country = formation.get("country", "N/A")
                    company_type = formation.get("company_type", "N/A")
                    formation_date = formation.get("constitution_date", "N/A")
                    registry = formation.get("registry", {})
                    
                    # Determine the source of the information
                    if registry is None:
                        if category == "cl_registral":
                            source = "Registral"
                        elif category == "cl_person" or category == "person":
                            source = "Persona natural"
                        else:
                            source = "Desconocida"
                    else:
                        if category == "cl_eud":
                            source = "Registro Electrónico"
                        else:
                            source = "Desconocida"

                    # Obtain administration stats
                    managers = administration.get("managers", [])
                    num_managers = len(managers)

                    # Obtain representatives stats
                    representatives = administration.get("sii_representatives", [])
                    num_representatives = len(representatives)

                    # Obtain equity stats
                    shareholders = equity.get("shareholders", [])
                    num_shareholders = len(shareholders)

                    # Determine participation total
                    total_participation = 0.0
                    for shareholder in shareholders:
                        participation_raw = shareholder.get("particitation", 0.0)
                        participation = float(participation_raw) if participation_raw is not None else 0.0
                        total_participation += participation

                    if total_participation <= 1.0:
                        total_participation = total_participation * 100

                    # Print out results
                    print(f"Número de actividades: {num_activities}")
                    print(f"País de constitución: {formation_country}")
                    print(f"Tipo de empresa: {company_type}")
                    print(f"Fecha de constitución: {formation_date}")
                    print(f"Número de gerentes: {num_managers}")
                    print(f"Número de representantes: {num_representatives}")
                    print(f"Número de accionistas: {num_shareholders}")
                    print(f"Total de participación de accionistas: {total_participation}%")
                    print(f"Fuente de datos del comercio: {source}")

                    stats_row = {
                        "RUT": rut,
                        "Actividades": num_activities,
                        "País": formation_country,
                        "Tipo_compañia": company_type,
                        "Fecha_constitución": formation_date,
                        "Gerentes": num_managers,
                        "Representantes": num_representatives,
                        "Accionistas": num_shareholders,
                        "Total_participación": total_participation,
                        "Fuente": source
                    }

                    self._append_stats_to_output(stats_row)


            # Else (report not found, 404, must create it)
            else:
                pass




            
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
        '''
        Run a validation workflow for Gesintel.
        '''
        
        # Get the client
        gesintel_client = get_gestintel_client()
        
        # Create the Gesintel controller using the client
        controller = GesintelController(gesintel_client)

        # Validate if the control columns exist
        self._validate_gestintel_watchlist_columns()

        # Get the size of the DataFrame
        total_rows = len(self.df)

        # Starting point for the frame
        initial_position = 0

        # Process by block
        block_size = 5

        # Move through the DataFrame (file) block by block according to definitions
        for start in range(initial_position, total_rows, block_size):
            end = min(start + block_size, total_rows)
            block = self.df.iloc[start:end]

            print(f"Procesando filas {start} to {end - 1}")

            # Within the block, extract the row and the index for each case
            for index, row in block.iterrows():
                rut = row['Rut']
                # print(f"Vamos a procesar comercio {rut}...")
                
                # Call the validation method. This returns a modified row if there are
                # changes, or nothing if not
                updated_row = controller.check_watchlists(row, index)

                # If the new row is not empty (that is, if it changed), replace it
                if updated_row is not None:
                    self.df.loc[index] = updated_row

            # input("Continuar...")
            self.save_to_excel()
            print("Esperando 2 segundos (para no superar el límite de consultas)...")
            time.sleep(2)


