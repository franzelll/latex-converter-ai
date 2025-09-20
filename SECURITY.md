# 🔒 Sicherheitsrichtlinien

## ⚠️ WICHTIG: API-Keys und Secrets

**NIE** API-Keys, Passwörter oder andere sensible Daten direkt in den Code committen!

### ✅ Sichere Verwendung von API-Keys:

#### 1. **Umgebungsvariablen verwenden**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ RICHTIG - Aus Umgebungsvariable laden
api_key = os.getenv('MISTRAL_API_KEY')
if not api_key:
    raise ValueError("MISTRAL_API_KEY nicht gesetzt!")
```

#### 2. **NIE direkt im Code**
```python
# ❌ FALSCH - Niemals so machen!
api_key = "sk-1234567890abcdef"  # NICHT SICHER!
```

### 🛡️ Sicherheitsmaßnahmen

#### **Für Git:**
- ✅ `.env` Dateien sind in `.gitignore`
- ✅ `env.example` zeigt erlaubte Variablen
- ✅ Keine hardcoded Secrets im Code

#### **Für Production:**
- ✅ Verwende sichere Secret-Management-Systeme
- ✅ Rotiere API-Keys regelmäßig
- ✅ Überwache API-Key-Nutzung

### 📋 Checkliste vor Git-Commit:

```bash
# 1. Prüfe auf hardcoded Secrets
grep -r "sk-\|api_key\|password\|secret" . --include="*.py"

# 2. Prüfe .env Dateien
ls -la .env*

# 3. Prüfe Git-Status
git status
```

### 🔧 Setup für sichere Entwicklung:

1. **Kopiere env.example zu .env:**
```bash
cp env.example .env
```

2. **Fülle echte Werte in .env ein:**
```bash
# .env (NICHT committen!)
MISTRAL_API_KEY=sk-dein-echter-api-key-hier
SECRET_KEY=dein-super-geheimer-schluessel
```

3. **Prüfe dass .env ignoriert wird:**
```bash
git status  # .env sollte NICHT erscheinen
```

### 🚨 Incident Response:

Falls ein API-Key versehentlich committed wurde:

1. **Sofort API-Key widerrufen** (bei Mistral)
2. **Neuen API-Key generieren**
3. **Git-History bereinigen** (falls nötig)
4. **Secrets rotieren**

### 📚 Weitere Sicherheitsrichtlinien:

- **Rate Limiting**: Schutz vor Missbrauch
- **Input Validation**: Schutz vor Injection-Attacken
- **HTTPS**: Verschlüsselte Kommunikation
- **Logging**: Keine Secrets in Logs
- **Monitoring**: Überwachung verdächtiger Aktivitäten

## 🔍 Security Scanning:

Das Projekt verwendet automatische Security-Scans:

```bash
# Safety Check
safety check

# Bandit Security Scan
bandit -r . -f json

# Dependency Check
pip-audit
```

---

**Erinnerung**: Sicherheit ist ein kontinuierlicher Prozess, nicht ein einmaliges Setup! 🔒
