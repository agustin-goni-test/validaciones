from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class DireccionPersonaNatural:
    address_date: str
    postal_code: str
    additional_info: str
    communes: str
    city: str
    number: str
    last_verification_date: str
    region: str
    street: str
    address_type: Optional[str]
    code_region: str
    source_of_address: str
    street_and_number: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            address_date=data.get("AddressDate", ""),
            postal_code=data.get("PostalCode", ""),
            additional_info=data.get("AditionalInfo", ""),
            communes=data.get("Communes", ""),
            city=data.get("City", ""),
            number=data.get("Number", ""),
            last_verification_date=data.get("LastAddressVerificationDate", ""),
            region=data.get("Region", ""),
            street=data.get("Street", ""),
            address_type=data.get("AddressType"),  # Can be None
            code_region=data.get("CodeRegion", ""),
            source_of_address=data.get("SourceOfAddress", ""),
            street_and_number=data.get("StreetAndNumber", "")
        )
    

@dataclass
class DireccionPersonaJuridica:
    addressDate: str
    addressType: str
    addressUpdateDate: str
    aditionalInfo: str
    city: str
    codeRegion: str
    communes: str
    lastAddressVerificationDate: str
    number: str
    postalCode: str
    region: str
    sourceOfAddress: str
    street: str
    streetAndNumber: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DireccionPersonaJuridica":
        return cls(
            addressDate=data.get("addressDate", ""),
            addressType=data.get("addressType", ""),
            addressUpdateDate=data.get("addressUpdateDate", ""),
            aditionalInfo=data.get("aditionalInfo", ""),
            city=data.get("city", ""),
            codeRegion=data.get("codeRegion", ""),
            communes=data.get("communes", ""),
            lastAddressVerificationDate=data.get("lastAddressVerificationDate", ""),
            number=data.get("number", ""),
            postalCode=data.get("postalCode", ""),
            region=data.get("region", ""),
            sourceOfAddress=data.get("sourceOfAddress", ""),
            street=data.get("street", ""),
            streetAndNumber=data.get("streetAndNumber", ""),
        )
