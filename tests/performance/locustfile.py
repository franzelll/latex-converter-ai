"""
Performance Tests mit Locust
"""
from locust import HttpUser, task, between


class LaTeXConverterUser(HttpUser):
    """Locust User für LaTeX Converter Performance Tests"""
    
    wait_time = between(1, 3)  # Wartezeit zwischen Anfragen
    
    def on_start(self):
        """Wird beim Start eines Users ausgeführt"""
        # Health Check
        response = self.client.get("/health")
        if response.status_code != 200:
            raise Exception("Service nicht verfügbar")
    
    @task(3)
    def health_check(self):
        """Health Check (häufig)"""
        self.client.get("/health")
    
    @task(2)
    def get_index(self):
        """Index-Seite laden (häufig)"""
        self.client.get("/")
    
    @task(1)
    def convert_simple_text(self):
        """Einfache Text-Konvertierung"""
        simple_text = """
# Einfaches Dokument

Dies ist ein **einfacher** Test-Text.

- Punkt 1
- Punkt 2

Normaler Absatz.
"""
        self.client.post("/", data={"text": simple_text})
    
    @task(1)
    def convert_complex_text(self):
        """Komplexe Text-Konvertierung"""
        complex_text = """
# Komplexes Dokument

Dies ist ein **komplexes** Dokument mit verschiedenen Elementen:

## Unterüberschrift

- **Wichtiger** Punkt
- *Kursiver* Punkt
- Normaler Punkt

### Detaillierte Unterüberschrift

| Spalte 1 | Spalte 2 | Spalte 3 |
|----------|----------|----------|
| Wert A   | Wert B   | Wert C   |
| Wert D   | Wert E   | Wert F   |

1. Erster Punkt
2. Zweiter Punkt
3. Dritter Punkt

Normaler Absatz mit viel Text. Dieser Absatz enthält genügend Inhalt um die 
Performance der Text-Verarbeitung zu testen. Er sollte verschiedene Aspekte 
der LaTeX-Konvertierung abdecken.

**Fetter Text** und *kursiver Text* werden ebenfalls getestet.

Ein weiterer Absatz mit verschiedenen Zeichen: ä ö ü ß und Sonderzeichen: ! ? . , ; :
"""
        self.client.post("/", data={"text": complex_text})
    
    @task(1)
    def test_special_characters(self):
        """Test mit Sonderzeichen"""
        special_text = """
# Sonderzeichen Test

Deutsche Umlaute: ä ö ü ß
Mathematische Zeichen: + - * / = < > ≤ ≥ ∞ ∑ ∫
Griechische Buchstaben: α β γ δ ε ζ η θ λ μ π ρ σ τ φ χ ψ ω
Punktuation: ! ? . , ; : " ' ( ) [ ] { } | \\ ~ ` @ # $ % ^ & _ + =
"""
        self.client.post("/", data={"text": special_text})
    
    @task(1)
    def test_table_heavy_document(self):
        """Dokument mit vielen Tabellen"""
        table_text = """
# Tabellen-reiches Dokument

| Header 1 | Header 2 | Header 3 | Header 4 |
|----------|----------|----------|----------|
| Zelle 1  | Zelle 2  | Zelle 3  | Zelle 4  |
| Zelle 5  | Zelle 6  | Zelle 7  | Zelle 8  |

## Zweite Tabelle

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 1 | 2 | 3 | 4 | 5 | 6 |
| 7 | 8 | 9 | 10| 11| 12|

### Dritte Tabelle

| Spalte A | Spalte B | Spalte C | Spalte D | Spalte E |
|----------|----------|----------|----------|----------|
| Wert 1   | Wert 2   | Wert 3   | Wert 4   | Wert 5   |
| Wert 6   | Wert 7   | Wert 8   | Wert 9   | Wert 10  |
| Wert 11  | Wert 12  | Wert 13  | Wert 14  | Wert 15  |
"""
        self.client.post("/", data={"text": table_text})
    
    @task(1)
    def test_large_list_document(self):
        """Dokument mit großen Listen"""
        list_text = """
# Listen-reiches Dokument

## Ungeordnete Liste
- Erster Punkt
- Zweiter Punkt
- Dritter Punkt
- Vierter Punkt
- Fünfter Punkt
- Sechster Punkt
- Siebter Punkt
- Achter Punkt
- Neunter Punkt
- Zehnter Punkt

## Geordnete Liste
1. Erster Punkt
2. Zweiter Punkt
3. Dritter Punkt
4. Vierter Punkt
5. Fünfter Punkt
6. Sechster Punkt
7. Siebter Punkt
8. Achter Punkt
9. Neunter Punkt
10. Zehnter Punkt

### Unterpunkte
- Hauptpunkt 1
  - Unterpunkt 1.1
  - Unterpunkt 1.2
    - Unter-Unterpunkt 1.2.1
    - Unter-Unterpunkt 1.2.2
- Hauptpunkt 2
  - Unterpunkt 2.1
  - Unterpunkt 2.2
"""
        self.client.post("/", data={"text": list_text})


class HighLoadUser(HttpUser):
    """User für hohe Last-Tests"""
    
    wait_time = between(0.5, 1.5)
    weight = 1  # Weniger häufig als normale User
    
    @task
    def rapid_requests(self):
        """Schnelle, einfache Anfragen"""
        simple_text = "# Quick Test\n\nQuick test content."
        self.client.post("/", data={"text": simple_text})
    
    @task
    def health_check(self):
        """Health Checks"""
        self.client.get("/health")
