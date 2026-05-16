from fpdf import FPDF
from typing import List
from ..models import Message

def generate_conversation_pdf(messages: List[Message], title: str, output_path: str) -> None:
    """
    Génère un fichier PDF contenant la conversation.
    
    Args:
        messages: Liste des messages de la conversation
        title: Titre du document
        output_path: Chemin de sortie du fichier PDF
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Titre
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    
    # Contenu
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for msg in messages:
        # En-tête du message (rôle + date)
        pdf.set_font("Arial", style="B", size=11)
        header = f"{msg.role.capitalize()} - {msg.created_at.strftime('%Y-%m-%d %H:%M')}"
        pdf.cell(0, 8, header, ln=True)
        
        # Contenu du message
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, msg.content)
        pdf.ln(4)
    
    pdf.output(output_path)