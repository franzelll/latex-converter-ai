from flask import Flask, render_template, request, send_file, flash, jsonify
import os
from latex_converter import LatexConverter
import tempfile
import traceback
import fitz  # PyMuPDF
from your_model_utils import simplify_text, simplify_text_batch, simplify_full_text  # Your model's simplify function
import concurrent.futures
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
from security import security_manager, require_security_validation, validate_latex_content
import logging
import time

# Umgebungsvariablen laden
load_dotenv()

app = Flask(__name__)

# Konfiguration aus Umgebungsvariablen
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # 10MB

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sicherheitsmanager initialisieren
security_manager.init_app(app)

# Set LaTeX compiler path
os.environ['PATH'] = '/Library/TeX/texbin:' + os.environ['PATH']

# Assume tokenizer and model are already loaded globally

@app.route('/health')
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'model_loaded': True,  # TODO: Prüfe ob Modell geladen ist
        'latex_available': True,  # TODO: Prüfe LaTeX-Installation
        'timestamp': time.time()
    })

@app.route('/', methods=['GET', 'POST'])
@require_security_validation
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.lower().endswith('.pdf'):
            with tempfile.TemporaryDirectory() as temp_dir:
                input_pdf_path = os.path.join(temp_dir, 'input.pdf')
                file.save(input_pdf_path)
                output_pdf_path = os.path.join(temp_dir, 'simplified.pdf')
                create_layout_preserving_simplified_pdf(input_pdf_path, output_pdf_path, target_language='de')
                return send_file(output_pdf_path, as_attachment=True, download_name='vereinfachtes_dokument.pdf', mimetype='application/pdf')
        try:
            # Get the text from the form
            text = request.form.get('text', '')
            
            if not text.strip():
                flash('Please enter some text to convert', 'error')
                return render_template('index.html')
            
            # Create a temporary directory for our files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create the converter
                converter = LatexConverter()
                
                # Process the text
                try:
                    # Text bereinigen
                    clean_text = security_manager.sanitize_text(text)
                    
                    # LaTeX-Inhalt validieren
                    is_valid, message = validate_latex_content(clean_text)
                    if not is_valid:
                        flash(f'Sicherheitsfehler: {message}', 'error')
                        return render_template('index.html')
                    
                    prompt = (
                        "Vereinfache den folgenden Text. "
                        "Schreibe ihn in einfachem Deutsch um, ohne etwas wegzulassen oder hinzuzufügen. "
                        "Gib nur den vereinfachten Text zurück, ohne weitere Erklärungen.\n\n"
                        f"Text:\n{clean_text}\n\nVereinfachter Text:\n"
                    )
                    converter.process_text(prompt)
                    logger.info(f"Text erfolgreich verarbeitet: {len(clean_text)} Zeichen")
                except Exception as e:
                    flash(f'Error processing text: {str(e)}', 'error')
                    return render_template('index.html')
                
                # Generate PDF
                pdf_path = os.path.join(temp_dir, 'output.pdf')
                try:
                    create_layout_preserving_simplified_pdf(pdf_path, converter.simplify_text, pdf_path)
                except Exception as e:
                    # Save the LaTeX source for debugging
                    tex_path = os.path.join(temp_dir, 'output.tex')
                    with open(tex_path, 'w', encoding='utf-8') as f:
                        f.write(converter.doc.dumps())
                    
                    # Read the LaTeX source
                    with open(tex_path, 'r', encoding='utf-8') as f:
                        latex_source = f.read()
                    
                    # Try to read the log file if it exists
                    log_path = os.path.join(temp_dir, 'output.log')
                    log_content = ""
                    if os.path.exists(log_path):
                        with open(log_path, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                    
                    error_msg = f"Error: {str(e)}\n\nLaTeX Source:\n{latex_source}\n\nLaTeX Log:\n{log_content}"
                    flash(error_msg, 'error')
                    return render_template('index.html')
                
                # Verify PDF exists before sending
                if not os.path.exists(pdf_path):
                    flash('PDF generation failed - no output file was created', 'error')
                    return render_template('index.html')
                
                # Send the file
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name='converted.pdf',
                    mimetype='application/pdf'
                )
                
        except Exception as e:
            # Get the full error traceback
            error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            flash(error_msg, 'error')
            return render_template('index.html')
    
    return render_template('index.html')

def create_layout_preserving_simplified_pdf(input_pdf_path, output_pdf_path, target_language='de'):
    doc = fitz.open(input_pdf_path)
    new_doc = fitz.open()
    # 1. Gesamten Fließtext extrahieren
    full_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    full_text += span["text"] + " "
        full_text += "\n"
    full_text = full_text.strip()
    print("EXTRAHIERTER TEXT:", full_text)
    # 2. Vereinfachen
    simplified = simplify_full_text(full_text, target_language=target_language)
    # 3. Neues PDF mit vereinfachtem Text
    for page_num in range(len(doc)):
        page_obj = new_doc.new_page(width=doc[page_num].rect.width, height=doc[page_num].rect.height)
        # Optional: Text auf mehrere Seiten aufteilen, falls zu lang
        page_obj.insert_textbox(
            fitz.Rect(0, 0, doc[page_num].rect.width, doc[page_num].rect.height),
            simplified,
            fontsize=12,
            fontname="helv",
            color=(0, 0, 0),
            align=0
        )
        break  # Nur auf erster Seite, oder Text aufteilen!
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()

def simplify_text_batch(texts, target_language='de'):
    prompts = [
        f"Vereinfache den folgenden Text in leicht verständliches, einfaches Deutsch. "
        f"Alle Informationen sollen erhalten bleiben, aber die Sätze sollen kürzer und klarer sein. "
        f"Schreibe den gesamten Text um, ohne etwas wegzulassen oder hinzuzufügen.\n\n"
        f"Text:\n{text}\n\nVereinfachter Text:"
        for text in texts
    ]
    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=512,
            temperature=0.5,
            top_p=0.8,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    split_key = "Vereinfachter Text:"
    simplified = [out.split(split_key)[-1].strip() for out in decoded]
    return simplified

def simplify_full_text(text, target_language='de'):
    prompt = f"Vereinfache folgenden Text auf einfachem Deutsch:\n\n{text}\n\nVereinfachter Text:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=2048)
    input_ids = inputs["input_ids"].to(model.device)
    attention_mask = inputs["attention_mask"].to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=1024,  # ggf. erhöhen für lange Texte
            temperature=0.5,
            top_p=0.8,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    split_key = "Vereinfachter Text:"
    simplified = decoded.split(split_key)[-1].strip()
    return simplified

if __name__ == '__main__':
    # Try different ports if 5000 is in use
    for port in range(5000, 5010):
        try:
            app.run(debug=True, port=port)
            break
        except OSError:
            continue 