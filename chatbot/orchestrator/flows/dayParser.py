import unicodedata
from rapidfuzz import process
class DayNormalizer:
    def __init__(self):
        self.CANONICAL_DAYS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        # 1. The "Rosetta Stone" Mapping
        # Keys are possible inputs (English, Portuguese, Abbreviations)
        # Values are the canonical Spanish day
        self.MAPPING = {
            # Spanish (Self-referential for typo fixing)
            'lunes': 'lunes', 'martes': 'martes', 'miercoles': 'miercoles', 
            'jueves': 'jueves', 'viernes': 'viernes', 'sabado': 'sabado', 'domingo': 'domingo',
            
            # English
            'monday': 'lunes', 'tuesday': 'martes', 'wednesday': 'miercoles',
            'thursday': 'jueves', 'friday': 'viernes', 'saturday': 'sabado', 'sunday': 'domingo',
            
            # Portuguese
            'segunda': 'lunes', 'segunda-feira': 'lunes',
            'terca': 'martes', 'terca-feira': 'martes',
            'quarta': 'miercoles', 'quarta-feira': 'miercoles',
            'quinta': 'jueves', 'quinta-feira': 'jueves',
            'sexta': 'viernes', 'sexta-feira': 'viernes',
            'sabado': 'sabado', # Same as Spanish
            'domingo': 'domingo', # Same as Spanish
            
            # Common Abbreviations (Optional)
            'mon': 'lunes', 'tue': 'martes', 'wed': 'miercoles',
            'seg': 'lunes', 'ter': 'martes', 'qua': 'miercoles'
        }

    def _clean_string(self, text: str) -> str:
        """Strips accents and lowers case (User's original logic + hyphen handling)"""
        text = text.strip().lower()
        # Remove accents
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        return text

    def normalize(self, input_day: str) -> str | None:
        clean_input = self._clean_string(input_day)
        
        # exact match
        if clean_input in self.MAPPING: 
            return self.MAPPING[clean_input]
            
        # rapidfuzz extractOne returns (match, score, index)
        match = process.extractOne(clean_input, self.MAPPING.keys())
        
        if match and match[1] > 80: # Score out of 100
            return self.MAPPING[match[0]]
            
        return None

# --- USAGE EXAMPLES ---

if __name__ == "__main__":
    normalizer = DayNormalizer()

    print(normalizer.normalize("Monday"))         # -> lunes
    print(normalizer.normalize("Terça-Feira"))    # -> martes
    print(normalizer.normalize("Miercoles"))      # -> miercoles
    print(normalizer.normalize("Miercolss"))      # -> miercoles (Typo fix)
    print(normalizer.normalize("Thurs day"))      # -> jueves (Space typo usually handled by fuzzy)
    print(normalizer.normalize("Sexta"))          # -> viernes