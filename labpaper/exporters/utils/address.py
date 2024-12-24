"""Address handling utilities."""
from dataclasses import dataclass
import usaddress


@dataclass
class Address:
    department: str = ''
    organization: str = ''
    street: str = ''
    city: str = ''
    state: str = ''
    postcode: str = ''
    country: str = ''
    
    @classmethod
    def from_string(cls, address_str: str):
        """Parse address from string using usaddress."""
        parts = [p.strip() for p in address_str.split(',')]
        addr = cls()
        
        # First part is always department
        if parts:
            addr.department = parts[0]
        
        # Second part is organization
        if len(parts) > 1:
            addr.organization = parts[1]
        
        # Try to parse the remaining parts as an address
        if len(parts) > 2:
            try:
                address_string = ', '.join(parts[2:])
                tagged_address, _ = usaddress.tag(address_string)
                
                addr.street = tagged_address.get('AddressNumber', '') + ' ' + \
                            tagged_address.get('StreetName', '') + ' ' + \
                            tagged_address.get('StreetNamePostType', '')
                addr.street = addr.street.strip()
                
                addr.city = tagged_address.get('PlaceName', '')
                addr.state = tagged_address.get('StateName', '')
                addr.postcode = tagged_address.get('ZipCode', '')
                
                # Country is usually the last part
                if len(parts) > 3:
                    addr.country = parts[-1].strip()
                
            except usaddress.RepeatedLabelError:
                # Fallback to simple parsing if address is complex
                if len(parts) > 2:
                    addr.street = parts[2]
                if len(parts) > 3:
                    addr.city = parts[3]
                if len(parts) > 4:
                    addr.state = parts[4]
                if len(parts) > 5:
                    addr.postcode = parts[5]
                if len(parts) > 6:
                    addr.country = parts[6]
        
        return addr
    
    def __eq__(self, other):
        """Compare two addresses for equality."""
        if not isinstance(other, Address):
            return NotImplemented
        return (
            self.department == other.department and
            self.organization == other.organization and
            self.street == other.street and
            self.city == other.city and
            self.state == other.state and
            self.postcode == other.postcode and
            self.country == other.country
        )

    def __hash__(self):
        """Hash function for Address instances."""
        return hash((
            self.department,
            self.organization,
            self.street,
            self.city,
            self.state,
            self.postcode,
            self.country
        ))

    def __repr__(self):
        """Detailed string representation."""
        parts = []
        if self.department:
            parts.append(f"dept='{self.department}'")
        if self.organization:
            parts.append(f"org='{self.organization}'")
        if self.street:
            parts.append(f"street='{self.street}'")
        if self.city:
            parts.append(f"city='{self.city}'")
        if self.state:
            parts.append(f"state='{self.state}'")
        if self.postcode:
            parts.append(f"postcode='{self.postcode}'")
        if self.country:
            parts.append(f"country='{self.country}'")
        
        return f"Address({', '.join(parts)})"