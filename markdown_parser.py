from mistune import Markdown, HTMLRenderer
import re

class LatexRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.table_alignments = []
        
    def table(self, header, body):
        # Process table header to determine alignments
        header_cells = re.findall(r'<th>(.*?)</th>', header)
        self.table_alignments = ['l'] * len(header_cells)
        
        # Convert HTML table to LaTeX
        latex = '\\begin{longtable}{' + ''.join(self.table_alignments) + '}\n'
        latex += '\\toprule\n'
        latex += header.replace('<th>', '').replace('</th>', ' & ').rstrip(' & ') + ' \\\\\n'
        latex += '\\midrule\n'
        latex += body.replace('<td>', '').replace('</td>', ' & ').rstrip(' & ') + ' \\\\\n'
        latex += '\\bottomrule\n'
        latex += '\\end{longtable}\n'
        return latex
        
    def heading(self, text, level):
        if level == 1:
            return f'\\section*{{{text}}}\n'
        elif level == 2:
            return f'\\subsection*{{{text}}}\n'
        else:
            return f'\\subsubsection*{{{text}}}\n'
            
    def list(self, body, ordered):
        if ordered:
            return f'\\begin{{enumerate}}\n{body}\\end{{enumerate}}\n'
        else:
            return f'\\begin{{itemize}}\n{body}\\end{{itemize}}\n'
            
    def list_item(self, text):
        return f'\\item {text}\n'
        
    def paragraph(self, text):
        return f'{text}\n\n'
        
    def text(self, text):
        # Escape special LaTeX characters
        text = text.replace('&', '\\&')
        text = text.replace('%', '\\%')
        text = text.replace('$', '\\$')
        text = text.replace('#', '\\#')
        text = text.replace('_', '\\_')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('~', '\\textasciitilde{}')
        text = text.replace('^', '\\textasciicircum{}')
        text = text.replace('\\', '\\textbackslash{}')
        return text

def convert_markdown_to_latex(markdown_text):
    renderer = LatexRenderer()
    markdown = Markdown(renderer=renderer)
    return markdown(markdown_text) 