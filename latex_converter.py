import os
import tempfile
import subprocess
from pylatex import Document, Section, Subsection, Command, Package
from pylatex.utils import NoEscape
from markdown_parser import convert_markdown_to_latex
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LatexConverter:
    """Konvertiert Text zu LaTeX und generiert PDFs"""
    
    def __init__(self):
        self.doc = None
        self.simplified_text = ""
        
    def process_text(self, text):
        """Verarbeitet Text und konvertiert zu LaTeX"""
        try:
            # Erstelle LaTeX-Dokument
            self.doc = Document(documentclass='article')
            
            # LaTeX-Pakete hinzufügen
            self.doc.packages.append(Package('inputenc', options=['utf8']))
            self.doc.packages.append(Package('booktabs'))
            self.doc.packages.append(Package('longtable'))
            self.doc.packages.append(Package('geometry', options=['margin=2.5cm']))
            self.doc.packages.append(Package('hyperref'))
            
            # Markdown zu LaTeX konvertieren
            latex_content = convert_markdown_to_latex(text)
            
            # Inhalt zum Dokument hinzufügen
            self.doc.append(NoEscape(latex_content))
            
            logger.info("Text erfolgreich zu LaTeX konvertiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der LaTeX-Konvertierung: {e}")
            raise
    
    def generate_pdf(self, output_path=None):
        """Generiert PDF aus LaTeX-Dokument"""
        try:
            if not self.doc:
                raise ValueError("Kein LaTeX-Dokument vorhanden")
            
            # Temporäres Verzeichnis für LaTeX-Kompilierung
            with tempfile.TemporaryDirectory() as temp_dir:
                # LaTeX-Datei generieren
                tex_file = os.path.join(temp_dir, 'document.tex')
                self.doc.generate_tex(tex_file)
                
                # PDF kompilieren
                result = subprocess.run([
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-output-directory', temp_dir,
                    tex_file
                ], capture_output=True, text=True, cwd=temp_dir)
                
                if result.returncode != 0:
                    logger.error(f"LaTeX-Kompilierung fehlgeschlagen: {result.stderr}")
                    raise RuntimeError(f"LaTeX-Fehler: {result.stderr}")
                
                # PDF-Datei kopieren
                pdf_file = os.path.join(temp_dir, 'document.pdf')
                if output_path:
                    import shutil
                    shutil.copy2(pdf_file, output_path)
                    logger.info(f"PDF generiert: {output_path}")
                    return output_path
                else:
                    return pdf_file
                    
        except Exception as e:
            logger.error(f"Fehler bei der PDF-Generierung: {e}")
            raise
    
    def simplify_text(self, text):
        """Vereinfacht Text (Placeholder für KI-Integration)"""
        # Diese Methode sollte mit dem AI-Modell integriert werden
        self.simplified_text = text
        return text
