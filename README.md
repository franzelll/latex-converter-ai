# 🚀 LaTeX Converter & Text Simplifier

Ein professioneller Web-Service, der Text in LaTeX konvertiert, PDFs generiert und mit KI-Unterstützung Texte vereinfacht.

## ✨ Features

### 🔄 **Text-Konvertierung**
- **Markdown zu LaTeX**: Vollständige Markdown-Unterstützung
- **Tabellen-Konvertierung**: Automatische LaTeX-Tabellen-Generierung
- **PDF-Export**: Hochwertige PDF-Dokumente
- **Unicode-Support**: Deutsche Zeichen und Sonderzeichen

### 🤖 **KI-Text-Vereinfachung**
- **Automatische Vereinfachung**: Komplexe Texte in einfaches Deutsch
- **Batch-Verarbeitung**: Mehrere Texte gleichzeitig verarbeiten
- **PDF-zu-PDF**: Direkte Vereinfachung von PDF-Dokumenten
- **Layout-Erhaltung**: Beibehaltung der ursprünglichen Formatierung

### 🌐 **Web-Interface**
- **Moderne UI**: Bootstrap-basierte Benutzeroberfläche
- **Drag & Drop**: Einfacher PDF-Upload
- **Echtzeit-Feedback**: Sofortige Fehlermeldungen
- **Responsive Design**: Mobile-optimiert

## 🛠️ Installation

### **Voraussetzungen**
- Python 3.9+
- LaTeX-Distribution (TeX Live, MiKTeX)
- 4GB+ RAM (für KI-Modell)

### **Schritt-für-Schritt Installation**

```bash
# 1. Repository klonen
git clone <repository-url>
cd code_try_latex

# 2. Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. LaTeX-Installation prüfen
pdflatex --version
```

### **LaTeX-Installation**

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-full
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
- [MiKTeX](https://miktex.org/download) herunterladen und installieren

## 🚀 Verwendung

### **Web-Service starten**
```bash
python app.py
```
Öffnen Sie `http://localhost:5000` im Browser.

### **API-Endpunkte**

#### **POST /** - Text zu PDF
```bash
curl -X POST http://localhost:5000 \
  -F "text=# Meine Überschrift\n\nDies ist ein Test-Text."
```

#### **POST /** - PDF vereinfachen
```bash
curl -X POST http://localhost:5000 \
  -F "file=@document.pdf"
```

### **Programmatische Nutzung**

```python
from latex_converter import LatexConverter
from your_model_utils import simplify_text

# Text zu LaTeX konvertieren
converter = LatexConverter()
converter.process_text("# Überschrift\n\nMein Text.")
pdf_path = converter.generate_pdf("output.pdf")

# Text vereinfachen
simplified = simplify_text("Komplexer Text mit vielen Fachbegriffen.")
```

## 📝 Eingabeformate

### **Markdown-Syntax**
```markdown
# Hauptüberschrift
## Unterüberschrift

**Fett** und *kursiv*

- Aufzählungspunkt 1
- Aufzählungspunkt 2

1. Nummerierte Liste
2. Zweiter Punkt

| Spalte 1 | Spalte 2 |
|----------|----------|
| Wert 1   | Wert 2   |
```

### **Unterstützte Features**
- ✅ Überschriften (H1-H6)
- ✅ Fett und kursiv
- ✅ Aufzählungen und nummerierte Listen
- ✅ Tabellen (mit Ausrichtung)
- ✅ Absätze und Zeilenumbrüche
- ✅ Deutsche Umlaute (ä, ö, ü, ß)
- ✅ Sonderzeichen

## ⚙️ Konfiguration

### **Umgebungsvariablen**
```bash
# .env Datei erstellen
MODEL_NAME=microsoft/phi-4-mini-instruct
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### **Modell-Konfiguration**
```python
# Verschiedene Modelle unterstützt:
# - microsoft/phi-4-mini-instruct (Standard)
# - microsoft/DialoGPT-medium
# - facebook/blenderbot-400M-distill
```

## 🧪 Testing

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=. --cov-report=html

# Spezifische Tests
pytest tests/test_latex_converter.py
pytest tests/test_model_utils.py
```

## 🐳 Docker

```bash
# Docker Image bauen
docker build -t latex-converter .

# Container starten
docker run -p 5000:5000 latex-converter
```

## 📊 Performance

### **Benchmarks**
- **Text-Konvertierung**: ~100ms pro Seite
- **PDF-Generierung**: ~500ms pro Seite
- **KI-Vereinfachung**: ~2-5s pro Absatz
- **Memory Usage**: ~2GB (mit Modell)

### **Optimierungen**
- Caching für wiederholte Anfragen
- Batch-Verarbeitung für mehrere Texte
- GPU-Beschleunigung (falls verfügbar)

## 🔧 Troubleshooting

### **Häufige Probleme**

**LaTeX-Fehler:**
```bash
# LaTeX-Installation prüfen
which pdflatex
pdflatex --version
```

**Modell-Ladefehler:**
```bash
# Speicher prüfen
free -h
# Modell-Größe reduzieren
export MODEL_NAME=microsoft/DialoGPT-small
```

**Port bereits belegt:**
```bash
# Anderen Port verwenden
python app.py --port 8080
```

## 🤝 Contributing

1. Fork das Repository
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` für Details.

## 🙏 Danksagungen

- [PyLaTeX](https://jeltef.github.io/PyLaTeX/) für LaTeX-Generierung
- [Transformers](https://huggingface.co/transformers/) für KI-Modelle
- [Flask](https://flask.palletsprojects.com/) für Web-Framework
- [Bootstrap](https://getbootstrap.com/) für UI

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Dokumentation**: [Wiki](https://github.com/your-repo/wiki)
- **Email**: support@your-domain.com

---

**Version**: 2.0.0  
**Letzte Aktualisierung**: 2025  
**Python**: 3.9+  
**LaTeX**: TeX Live 2023+ 