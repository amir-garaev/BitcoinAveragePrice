import os
from dotenv import load_dotenv
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

bitcoin_address_regex = r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$"