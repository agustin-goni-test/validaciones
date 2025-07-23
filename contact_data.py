from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class PhoneNumberJuridica:
    country_code: str
    area_code: str
    source_description: str
    last_update: str
    number: str
    subtype: str
    validation_date: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            country_code=data.get("codCountry", ""),
            area_code=data.get("codeArea", ""),
            source_description=data.get("descInfoSource", ""),
            last_update=data.get("lastUpdate", ""),
            number=data.get("referencyDesc", ""),
            subtype=data.get("referencyDescSubType", ""),
            validation_date=data.get("validationDate", "")
        )


@dataclass
class EmailJuridica:
    source_description: str
    last_update: str
    email: str
    subtype: str
    validation_date: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            source_description=data.get("descInfoSource", ""),
            last_update=data.get("lastUpdate", ""),
            email=data.get("referencyDesc", ""),
            subtype=data.get("referencyDescSubType", ""),
            validation_date=data.get("validationDate", "")
        )


@dataclass
class ContactDataSummaryJuridica:
    address_count: int
    date_last_address: str
    email_last_date: str
    last_email: str
    last_telephone: str
    last_website: str
    telephone_last_date: str
    total_email: int
    total_telephone: int
    total_website: int
    website_last_date: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            address_count=int(data.get("addressCount", 0)),
            date_last_address=data.get("dateLastAddress", ""),
            email_last_date=data.get("emailLastDate", ""),
            last_email=data.get("lastEmail", ""),
            last_telephone=data.get("lastTelephone", ""),
            last_website=data.get("lastWebsite", ""),
            telephone_last_date=data.get("telephoneLastDate", ""),
            total_email=int(data.get("totalEmail", 0)),
            total_telephone=int(data.get("totalTelephone", 0)),
            total_website=int(data.get("totalWebsite", 0)),
            website_last_date=data.get("websiteLastDate", "")
        )



@dataclass
class PhoneNumberNatural:
    telephone: int
    source_of_telephone: str
    telephone_date: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            telephone=data.get("Telephone", 0),
            source_of_telephone=data.get("SourceOfTelephone", ""),
            telephone_date=data.get("TelephoneDate", "")
        )