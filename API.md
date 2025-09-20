# 📚 API Dokumentation

## Übersicht

Die LaTeX Converter API bietet Endpunkte zur Konvertierung von Text zu PDF und zur Vereinfachung von PDF-Dokumenten.

**Base URL**: `http://localhost:5000`

## Endpunkte

### POST / - Text zu PDF konvertieren

Konvertiert Markdown-Text zu PDF-Dokument.

#### Request

**Content-Type**: `multipart/form-data`

| Parameter | Typ | Beschreibung | Erforderlich |
|-----------|-----|--------------|--------------|
| `text` | string | Markdown-Text zum Konvertieren | Ja |

#### Request Body Example

```bash
curl -X POST http://localhost:5000 \
  -F "text=# Meine Überschrift

Dies ist ein **wichtiger** Text mit einer Tabelle:

| Spalte 1 | Spalte 2 |
|----------|----------|
| Wert A   | Wert B   |"
```

#### Response

**Success (200 OK)**
- **Content-Type**: `application/pdf`
- **Body**: PDF-Datei als Binary

**Error (200 OK)**
- **Content-Type**: `text/html`
- **Body**: HTML-Seite mit Fehlermeldung

#### Error Codes

| Code | Beschreibung |
|------|--------------|
| 200 | Success oder Error (siehe Body) |
| 500 | Server Error |

---

### POST / - PDF vereinfachen

Vereinfacht ein PDF-Dokument mit KI-Unterstützung.

#### Request

**Content-Type**: `multipart/form-data`

| Parameter | Typ | Beschreibung | Erforderlich |
|-----------|-----|--------------|--------------|
| `file` | file | PDF-Datei zum Vereinfachen | Ja |

#### Request Body Example

```bash
curl -X POST http://localhost:5000 \
  -F "file=@document.pdf"
```

#### Response

**Success (200 OK)**
- **Content-Type**: `application/pdf`
- **Body**: Vereinfachte PDF-Datei als Binary

**Error (200 OK)**
- **Content-Type**: `text/html`
- **Body**: HTML-Seite mit Fehlermeldung

---

## Datenmodelle

### Text Input Format

Unterstützte Markdown-Syntax:

```markdown
# Hauptüberschrift
## Unterüberschrift
### Unter-Unterüberschrift

**Fett** und *kursiv*

- Aufzählungspunkt 1
- Aufzählungspunkt 2

1. Nummerierte Liste
2. Zweiter Punkt

| Spalte 1 | Spalte 2 | Spalte 3 |
|----------|----------|----------|
| Wert A   | Wert B   | Wert C   |
| Wert D   | Wert E   | Wert F   |

Normaler Absatz mit Text.

Neuer Absatz nach Leerzeile.
```

### PDF Output

Generierte PDFs verwenden:
- **Document Class**: `article`
- **Packages**: `inputenc`, `booktabs`, `longtable`, `geometry`, `hyperref`
- **Encoding**: UTF-8
- **Margins**: 2.5cm

## Fehlerbehandlung

### Häufige Fehler

#### LaTeX Compilation Error
```json
{
  "error": "LaTeX compilation failed",
  "details": "Undefined control sequence",
  "latex_log": "..."
}
```

#### Model Loading Error
```json
{
  "error": "Model loading failed",
  "details": "CUDA out of memory"
}
```

#### File Upload Error
```json
{
  "error": "Invalid file format",
  "details": "Expected PDF file"
}
```

## Rate Limits

- **Text Processing**: 10 requests/minute
- **PDF Processing**: 5 requests/minute
- **File Size Limit**: 10MB

## Authentication

Derzeit keine Authentication erforderlich. Für Produktionsumgebungen wird API-Key Authentication empfohlen.

## SDKs und Libraries

### Python

```python
import requests

def convert_text_to_pdf(text):
    response = requests.post(
        'http://localhost:5000',
        files={'text': text}
    )
    return response.content

def simplify_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        response = requests.post(
            'http://localhost:5000',
            files={'file': f}
        )
    return response.content
```

### JavaScript

```javascript
async function convertTextToPDF(text) {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await fetch('http://localhost:5000', {
        method: 'POST',
        body: formData
    });
    
    return response.blob();
}

async function simplifyPDF(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:5000', {
        method: 'POST',
        body: formData
    });
    
    return response.blob();
}
```

### cURL

```bash
# Text zu PDF
curl -X POST http://localhost:5000 \
  -F "text=# Meine Überschrift\n\nMein Text." \
  -o output.pdf

# PDF vereinfachen
curl -X POST http://localhost:5000 \
  -F "file=@document.pdf" \
  -o simplified.pdf
```

## Performance

### Benchmarks

| Operation | Durchschnittliche Zeit | Memory Usage |
|-----------|----------------------|--------------|
| Text zu PDF (1 Seite) | 100ms | 50MB |
| Text zu PDF (10 Seiten) | 800ms | 200MB |
| PDF vereinfachen (1 Seite) | 2-5s | 500MB |
| PDF vereinfachen (10 Seiten) | 20-50s | 2GB |

### Optimierungen

1. **Caching**: Identische Anfragen werden gecacht
2. **Batch Processing**: Mehrere Texte gleichzeitig verarbeiten
3. **GPU Acceleration**: Automatische GPU-Nutzung falls verfügbar
4. **Memory Management**: Automatische Speicherbereinigung

## Monitoring

### Health Check

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "model_loaded": true,
  "latex_available": true
}
```

### Metrics

- **Request Count**: Anzahl der Anfragen
- **Processing Time**: Verarbeitungszeit pro Anfrage
- **Error Rate**: Fehlerrate
- **Memory Usage**: Speichernutzung
- **Model Performance**: KI-Modell Performance

## Changelog

### Version 2.0.0
- ✅ KI-Text-Vereinfachung hinzugefügt
- ✅ PDF-zu-PDF Konvertierung
- ✅ Verbesserte Fehlerbehandlung
- ✅ Performance-Optimierungen

### Version 1.0.0
- ✅ Grundlegende Markdown-zu-PDF Konvertierung
- ✅ Web-Interface
- ✅ Tabellen-Support
