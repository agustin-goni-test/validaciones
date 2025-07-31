from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Any
import json
from dateutil.parser import parse


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