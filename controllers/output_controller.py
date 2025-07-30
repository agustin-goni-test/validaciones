import json
import pandas as pd
import os

class OutputController:
    def __init__(
                self,
                csv_file: str = None,
                excel_file: str = None,
                txt_file: str = None,
                output_folder: str = None
            ):
        self.cvs_output = csv_file
        self.xlsx_output = excel_file
        self.txt_output = txt_file
        self.output_folder = output_folder if output_folder else "output_files"
        self.data = []
        self.csv_enabled = False
        self.excel_enabled = False
        self.txt_enabled = False


    def _initialize_output_folder(self):
        """
        Initializes the output folder if it does not exist.
        """
        
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"Output folder created: {self.output_folder}")
        else:
            print(f"Output folder already exists: {self.output_folder}")


    def initialize_output_files(self):
        """
        Initializes the output files based on the selected formats.
        """
        self._initialize_output_folder()

        if self.csv_enabled and self.cvs_output:
            self.cvs_output = os.path.join(self.output_folder, self.cvs_output)
        
        if self.excel_enabled and self.xlsx_output:
            self.xlsx_output = os.path.join(self.output_folder, self.xlsx_output)
        
        if self.txt_enabled and self.txt_output:
            self.txt_output = os.path.join(self.output_folder, self.txt_output)

    
    def write_output(self, data: list):
        """
        Writes the output data to the selected formats.
        The input is a list of strings or dictionaries.
        """

        # If TXT is selected and txt file exists, call method that writes line to txt
        if self.txt_enabled and self.txt_output:
            self._write_to_txt(data)


    def _write_to_txt(self, data: list):
        '''This method writes data to a TXT file
        The input is a list of string, to be written in one line, separated by two hypens ("--")'''

        # Make sure this output is appended to file
        with open(self.txt_output, 'a') as f:
            # Write each string in the data and then add separator
            for item in data:
                f.write(f"{item} -- ")
            f.write("\n")  # New line after each entry   




    def select_output_format(self, csv_enabled: bool, excel_enabled: bool, txt_enabled: bool = False):
        """
        Selects the output format for the data.
        """
        self.csv_enabled = csv_enabled
        self.excel_enabled = excel_enabled
        self.txt_enabled = txt_enabled

        if not self.csv_enabled and not self.excel_enabled and not txt_enabled:
            raise ValueError("Debe seleccionar al menos un formato de salida (CSV, TXT o Excel).")
        
        if self.csv_enabled:
            if not self.cvs_output:
                raise ValueError("Debe proporcionar un archivo CSV de salida.")
            print(f"Formato de salida seleccionado: CSV={self.csv_enabled}, Excel={self.excel_enabled}")
        
        if self.excel_enabled:  
            if not self.xlsx_output:
                raise ValueError("Debe proporcionar un archivo Excel de salida.")
            print(f"Formato de salida seleccionado: CSV={self.csv_enabled}, Excel={self.excel_enabled}")

        if self.txt_enabled:
            if not self.txt_output:
                raise ValueError("Debe proporcionar un archivo TXT de salida.")
            print(f"Formato de salida seleccionado: CSV={self.csv_enabled}, Excel={self.excel_enabled}, TXT={self.txt_enabled}")
        
        print(f"Formato de salida seleccionado: CSV={self.csv_enabled}, Excel={self.excel_enabled}")

        self.initialize_output_files()


    
    def add_header(self, header: list):
        """
        Adds a header to the output data.
        """
        self.data.append(header)

    
    def add_entry(self, entry: dict):
        self.data.append(entry)


    def save_to_csv(self):
        with open(self.cvs_output, 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"Data saved to {self.output_file}")


    def save_to_excel(self):
        df = pd.DataFrame(self.data)
        df.to_excel(self.xlsx_output, index=False)
        print(f"Data saved to {self.xlsx_output}")

    
    def generate_output(self):
        """
        Generates the output file.
        """
        # Save to CSV
        self.save_to_csv()

        # Save to Excel
        self.save_to_excel()

        print(f"Output generated in {self.output_folder}")