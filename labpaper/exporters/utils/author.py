"""Author handling utilities."""

import re
from dataclasses import dataclass, field
from typing import List, Optional
from nameparser import HumanName

from .affiliation import Affiliation

@dataclass
class Author:
    index: int
    given_name: str
    surname: str
    email: Optional[str] = None
    particle: Optional[str] = None  # van der, de, etc.
    suffix: Optional[str] = None    # Jr., III, etc.
    affiliations: List[int] = field(default_factory=list)
    is_corresponding: bool = False
    equal_contribution: bool = False

    def __eq__(self, other):
        """Compare two authors for equality."""
        if not isinstance(other, Author):
            return NotImplemented
        return (
            self.given_name == other.given_name and
            self.surname == other.surname and
            self.email == other.email and
            self.particle == other.particle and
            self.suffix == other.suffix and
            sorted(self.affiliations) == sorted(other.affiliations) and
            self.is_corresponding == other.is_corresponding and
            self.equal_contribution == other.equal_contribution
        )

    def __hash__(self):
        """Hash function for Author instances."""
        return hash((
            self.given_name,
            self.surname,
            self.email,
            self.particle,
            self.suffix,
            tuple(sorted(self.affiliations)),
            self.is_corresponding,
            self.equal_contribution
        ))

    def __repr__(self):
        """Detailed string representation."""
        name = f"{self.given_name} {self.surname}"
        if self.suffix:
            name += f", {self.suffix}"
        return (
            f"Author("
            f"name='{name}', "
            f"email={self.email!r}, "
            f"affiliations={self.affiliations}, "
            f"corresponding={self.is_corresponding}, "
            f"equal_contrib={self.equal_contribution}"
            f")"
        )

def parse_authors_section(cell_source: str) -> tuple[List[Author], List[Affiliation]]:
    """Parse authors section from markdown cell."""
    authors = []
    affiliation_list = []   # Store affiliations in order
    this_author = None
    
    # Find the authors section
    author_section_match = re.search(
        r'^Authors?:\s*\n((?:.+\n(?:\s+.+\n)*)+)',
        cell_source,
        re.MULTILINE
    )
    
    if not author_section_match:
        return [], []
    
    # Split into lines and process them
    lines = [line.rstrip() for line in author_section_match.group(1).splitlines()]
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            break
        # Determine if this is an author line or a affiliation
        is_authorline = not (line.startswith(' ') or line.startswith('\t'))        
        if is_authorline:
            author_match = re.match(r'(\d+)\.\s*([!*]*)?(.+?)(?:,\s*(?!e:)(.+?))?(?:\s+e:\s*(\S+@\S+))?\s*$', stripped_line)
            if author_match:
                _, qualifiers, name_str, suffix, email = author_match.groups()
                author_name = HumanName(name_str.strip())
                this_author = Author(
                    index= int(len(authors)+1),
                    given_name=author_name.first,
                    particle=author_name.middle,
                    surname=author_name.last,
                    suffix=suffix,
                    email=email,
                    is_corresponding=bool(qualifiers and '*' in qualifiers),
                    equal_contribution=bool(qualifiers and '!' in qualifiers)
                )
                if this_author not in authors:
                    authors.append(this_author)
                # If we located an author, we can continue to the next line to determine their affiliations
                continue
        # We should only make it here if we are on an affiliation line
        affil_match = re.match(r'\s*(\d+)\.\s+(.+)$', stripped_line)
        
        this_affil_id = int(len(affiliation_list)+1)
        this_affil = Affiliation(
            id=this_affil_id,
            address=affil_match.group(2)
        )
        # If not already in the list, add it, then send the index to the author
        if this_affil not in affiliation_list:
            affiliation_list.append(this_affil)
            authors[-1].affiliations.append(this_affil.id)
        else:
            # Determine which affiliation index is in the list already
            for i, affil in enumerate(affiliation_list):
                if affil == this_affil:
                    authors[-1].affiliations.append(affil.id)
                    break
    
    return authors, affiliation_list