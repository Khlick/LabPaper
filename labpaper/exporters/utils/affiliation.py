"""Affiliation handling utilities."""
from dataclasses import dataclass
from .address import Address
    
@dataclass
class Affiliation:
    id: int
    address: Address
    
    def __init__(self, id: int, address: str):
        self.id = id
        self.address = Address.from_string(address)

    def __eq__(self, other):
        """Compare two affiliations for equality."""
        if not isinstance(other, Affiliation):
            return NotImplemented
        # Compare only based on address since id may be inconsistent
        return (
            self.address == other.address
        )

    def __hash__(self):
        """Hash function for Affiliation instances."""
        return hash((self.address))

    def __repr__(self):
        """Detailed string representation."""