from dotenv import load_dotenv
from clients.equifax_client import get_equifax_client


load_dotenv()

def main():

    print("Token tests")

    equifax_client = get_equifax_client()

    equifax_client.set_token_origin("auth")

    informe = equifax_client.obtain_report_corporation("764311612")

    print(informe)

if __name__ == '__main__':
    main()
