#!/bin/bash
# Security Check Script für LaTeX Converter

echo "🔒 Security Check für LaTeX Converter"
echo "====================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktion für gefärbten Output
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
echo "1. Prüfe auf hardcoded Secrets..."
echo "--------------------------------"

# Prüfe auf häufige Secret-Patterns (ohne venv/)
SECRETS_FOUND=0

# API Keys (ohne venv/, Kommentare und Docstrings)
if find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec grep -H "sk-[a-zA-Z0-9]" {} \; 2>/dev/null | grep -v "#" | grep -v "comment" | grep -v "example" | grep -v '"""' | grep -v "Tests für"; then
    print_status "Hardcoded API Keys gefunden!" 1
    SECRETS_FOUND=1
fi

# Passwords (ohne venv/ und Kommentare)
if find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec grep -H "password\s*=\s*[\"'][^\"']*[\"']" {} \; 2>/dev/null | grep -v "#" | grep -v "comment" | grep -v "example"; then
    print_status "Hardcoded Passwörter gefunden!" 1
    SECRETS_FOUND=1
fi

# Secrets (ohne venv/ und Kommentare)
if find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec grep -H "secret\s*=\s*[\"'][^\"']*[\"']" {} \; 2>/dev/null | grep -v "#" | grep -v "comment" | grep -v "example" | grep -v "your-secret-key"; then
    print_status "Hardcoded Secrets gefunden!" 1
    SECRETS_FOUND=1
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    print_status "Keine hardcoded Secrets gefunden" 0
fi

echo ""
echo "2. Prüfe .env Dateien..."
echo "------------------------"

# Prüfe ob .env Dateien existieren
if [ -f ".env" ]; then
    print_warning ".env Datei gefunden - stelle sicher, dass sie nicht committed wird"
    if git check-ignore .env >/dev/null 2>&1; then
        print_status ".env wird von Git ignoriert" 0
    else
        print_status ".env wird NICHT von Git ignoriert!" 1
    fi
else
    print_status "Keine .env Datei gefunden" 0
fi

echo ""
echo "3. Prüfe .gitignore..."
echo "---------------------"

# Prüfe wichtige .gitignore Einträge
if grep -q "\.env" .gitignore; then
    print_status ".env in .gitignore" 0
else
    print_status ".env NICHT in .gitignore!" 1
fi

if grep -q "\*secret\*" .gitignore; then
    print_status "Secret-Pattern in .gitignore" 0
else
    print_status "Secret-Pattern NICHT in .gitignore!" 1
fi

echo ""
echo "4. Prüfe Git-Status..."
echo "---------------------"

# Prüfe ob sensible Dateien staged sind
if git status --porcelain | grep -E "\.(env|key|secret)"; then
    print_status "Sensible Dateien sind staged!" 1
else
    print_status "Keine sensiblen Dateien staged" 0
fi

echo ""
echo "5. Prüfe Dependencies..."
echo "----------------------"

# Prüfe auf bekannte Sicherheitslücken
if command -v safety >/dev/null 2>&1; then
    if safety check >/dev/null 2>&1; then
        print_status "Safety Check bestanden" 0
    else
        print_status "Safety Check fehlgeschlagen!" 1
        echo "Führe 'safety check' für Details aus"
    fi
else
    print_warning "Safety nicht installiert - führe 'pip install safety' aus"
fi

echo ""
echo "6. Prüfe Code-Sicherheit..."
echo "-------------------------"

# Prüfe auf häufige Sicherheitsprobleme (ohne venv/)
if find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -exec grep -l "subprocess\|os\.system\|eval\|exec" {} \; 2>/dev/null; then
    print_warning "Potentiell unsichere Funktionen gefunden - überprüfe manuell"
fi

echo ""
echo "7. Zusammenfassung..."
echo "===================="

if [ $SECRETS_FOUND -eq 0 ]; then
    print_status "Security Check bestanden! 🎉" 0
    echo ""
    echo "Die Anwendung ist bereit für Git-Commit."
    echo ""
    echo "Nächste Schritte:"
    echo "1. Erstelle .env Datei mit echten API-Keys"
    echo "2. Teste die Anwendung lokal"
    echo "3. Committe zu Git"
else
    print_status "Security Check fehlgeschlagen! 🚨" 1
    echo ""
    echo "Bitte behebe die gefundenen Sicherheitsprobleme bevor du committest!"
fi

echo ""
echo "Für weitere Informationen siehe SECURITY.md"
