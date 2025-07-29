from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Any
import json
from dateutil.parser import parse


# @dataclass
# class ListMatch:
#     id: str
#     hit_id: str
#     date: str
#     category: str
#     source: str
#     listing: str
#     program: str
#     remarks: Optional[str]
#     country: str
#     position: Optional[str]
#     created_at: str
#     updated_at: str
#     false_positive: bool
#     false_positive_by_id: Optional[str]
#     type: Optional[str]

#     @classmethod
#     def from_json(cls, data: dict) -> "ListMatch":
#         return cls(
#             id=data["id"],
#             hit_id=data["hit_id"],
#             date=data["date"],
#             category=data["category"],
#             source=data["source"],
#             listing=data.get("listing"),
#             program=data["program"],
#             remarks=data["remarks"],
#             country=data["country"],
#             position=data.get("position"),
#             created_at=data.get("created_at"),
#             updated_at=data.get("updated_at"),
#             false_positive=data.get("false_positive", False),
#             false_positive_by_id=data.get("false_positive_by_id"),
#             type=data.get("type"),
#         )



# @dataclass
# class Hit:
#     id: str
#     full_name: str
#     match_types: List[Any]
#     list_types: List[Any]
#     score: float
#     risk_level: Optional[str]
#     hit_type: str
#     countries: List[Any]
#     list_matches: List[ListMatch]

#     @staticmethod
#     def from_json(data: dict) -> 'Hit':
#         list_matches_data = data.get("list_matches", [])
#         list_matches = [ListMatch.from_json(match) for match in list_matches_data]
        
#         return cls(
#             id=data["id"],
#             full_name=data["full_name"],
#             match_types=data.get("match_types", []),
#             list_types=data.get("list_types", []),
#             score=data.get("score", 0.0),
#             risk_level=data.get("risk_level"),
#             hit_type=data.get("hit_type"),
#             countries=data.get("countries", []),
#             list_matches=list_matches,
#             created_at=data.get("created_at"),
#             updated_at=data.get("updated_at"),
#             false_positive=data.get("false_positive", False),
#             false_positive_by_id=data.get("false_positive_by_id"),
#             type=data.get("type"),
#         )


# @dataclass
# class Watchlist:
#     id: str
#     total_hits: int
#     total_blacklist_hits: int
#     total_matches: int
#     share_url: Optional[str]
#     risk_level: str
#     watchlistable_name: str
#     source: str
#     created_at: str
#     updated_at: str
#     entity_validation_id: str
#     entity_validation_tin: str
#     hits: List[Hit]

#     @staticmethod
#     def from_json(data: dict) -> 'Watchlist':
#         hits_data = data.get("hits", [])
#         hits = [Hit.from_json(hit) for hit in hits_data]
#         return Watchlist(
#             id=data["id"],
#             total_hits=data["total_hits"],
#             total_blacklist_hits=data["total_blacklist_hits"],
#             total_matches=data["total_matches"],
#             share_url=data.get("share_url"),
#             risk_level=data["risk_level"],
#             watchlistable_name=data["watchlistable_name"],
#             source=data["source"],
#             created_at=data["created_at"],
#             updated_at=data["updated_at"],
#             entity_validation_id=data["entity_validation_id"],
#             entity_validation_tin=data["entity_validation_tin"],
#             hits=hits
#         )


# @dataclass
# class WatchlistResponse:
#     watchlists: List[Watchlist]

#     @staticmethod
#     def from_json(data: dict) -> 'WatchlistResponse':
#         watchlists = [Watchlist.from_json(w) for w in data.get("watchlists", [])]
#         return WatchlistResponse(watchlists=watchlists)

#     def to_json(self, indent: Optional[int] = None) -> str:
#         return json.dumps(asdict(self), indent=indent)


# class ListMatch:
#     def __init__(self, data: dict):
#         self.id = data.get('id')
#         self.hit_id = data.get('hit_id')
#         self.date = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None
#         self.category = data.get('category')
#         self.source = data.get('source')
#         self.listing = data.get('listing')
#         self.program = data.get('program')
#         self.remarks = data.get('remarks')
#         self.country = data.get('country')
#         self.position = data.get('position')
#         self.created_at = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('created_at') else None
#         self.updated_at = datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('updated_at') else None
#         self.false_positive = data.get('false_positive', False)
#         self.false_positive_by_id = data.get('false_positive_by_id')
#         self.type = data.get('type')

#     def __repr__(self):
#         return f"ListMatch(id={self.id}, category={self.category}, source={self.source})"

# class Hit:
#     def __init__(self, data: dict):
#         self.id = data.get('id')
#         self.full_name = data.get('full_name')
#         self.match_types = data.get('match_types', [])
#         self.list_types = data.get('list_types', [])
#         self.score = data.get('score', 0.0)
#         self.risk_level = data.get('risk_level')
#         self.hit_type = data.get('hit_type')
#         self.countries = data.get('countries', [])
#         self.list_matches = [ListMatch(match) for match in data.get('list_matches', [])]

#     def __repr__(self):
#         return f"Hit(id={self.id}, full_name={self.full_name}, matches={len(self.list_matches)})"

# class Watchlist:
#     def __init__(self, data: dict):
#         self.id = data.get('id')
#         self.total_hits = data.get('total_hits', 0)
#         self.total_blacklist_hits = data.get('total_blacklist_hits', 0)
#         self.total_matches = data.get('total_matches', 0)
#         self.share_url = data.get('share_url')
#         self.risk_level = data.get('risk_level')
#         self.watchlistable_name = data.get('watchlistable_name')
#         self.source = data.get('source')
#         self.created_at = datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('created_at') else None
#         self.updated_at = datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get('updated_at') else None
#         self.entity_validation_id = data.get('entity_validation_id')
#         self.entity_validation_tin = data.get('entity_validation_tin')
#         self.hits = [Hit(hit) for hit in data.get('hits', [])]

#     def __repr__(self):
#         return f"Watchlist(id={self.id}, name={self.watchlistable_name}, hits={len(self.hits)})"

# class WatchlistResponse:
#     def __init__(self, data: dict):
#         self.watchlists = [Watchlist(wl) for wl in data.get('watchlists', [])]

#     def __repr__(self):
#         return f"WatchlistResponse(watchlists={len(self.watchlists)})"

#     @classmethod
#     def from_json(cls, json_str: str):
#         import json
#         data = json.loads(json_str)
#         return cls(data)


class ListMatch:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.hit_id = data.get('hit_id')
        self.date = parse(data['date']).date() if data.get('date') else None
        self.category = data.get('category')
        self.source = data.get('source')
        self.listing = data.get('listing')
        self.program = data.get('program')
        self.remarks = data.get('remarks')
        self.country = data.get('country')
        self.position = data.get('position')
        self.created_at = parse(data['created_at']) if data.get('created_at') else None
        self.updated_at = parse(data['updated_at']) if data.get('updated_at') else None
        self.false_positive = data.get('false_positive', False)
        self.false_positive_by_id = data.get('false_positive_by_id')
        self.type = data.get('type')

    def __repr__(self):
        return f"ListMatch(id={self.id}, category={self.category}, source={self.source})"

class Hit:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.full_name = data.get('full_name')
        self.match_types = data.get('match_types', [])
        self.list_types = data.get('list_types', [])
        self.score = data.get('score', 0.0)
        self.risk_level = data.get('risk_level')
        self.hit_type = data.get('hit_type')
        self.countries = data.get('countries', [])
        self.list_matches = [ListMatch(match) for match in data.get('list_matches', [])]

    def __repr__(self):
        return f"Hit(id={self.id}, full_name={self.full_name}, matches={len(self.list_matches)})"

class Watchlist:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.total_hits = data.get('total_hits', 0)
        self.total_blacklist_hits = data.get('total_blacklist_hits', 0)
        self.total_matches = data.get('total_matches', 0)
        self.share_url = data.get('share_url')
        self.risk_level = data.get('risk_level')
        self.watchlistable_name = data.get('watchlistable_name')
        self.source = data.get('source')
        self.created_at = parse(data['created_at']) if data.get('created_at') else None
        self.updated_at = parse(data['updated_at']) if data.get('updated_at') else None
        self.entity_validation_id = data.get('entity_validation_id')
        self.entity_validation_tin = data.get('entity_validation_tin')
        self.hits = [Hit(hit) for hit in data.get('hits', [])]

    def __repr__(self):
        return f"Watchlist(id={self.id}, name={self.watchlistable_name}, hits={len(self.hits)})"

class WatchlistResponse:
    def __init__(self, data: dict):
        self.watchlists = [Watchlist(wl) for wl in data.get('watchlists', [])]

    def __repr__(self):
        return f"WatchlistResponse(watchlists={len(self.watchlists)})"

    @classmethod
    def from_json(cls, json_input):
        """Accepts either a JSON string or already-parsed dictionary"""
        if isinstance(json_input, str):
            data = json.loads(json_input)
        elif isinstance(json_input, dict):
            data = json_input
        else:
            raise ValueError("Input must be JSON string or dictionary")
        return cls(data)