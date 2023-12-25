from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import locale
from unidecode import unidecode
from datetime import datetime
from apicore.models import  Animal, CostsCategory, Species

def getAnimalName(id):
    animal = Animal.objects.filter(id=id).first()
    return animal.name
def getCostCategoryName(id):
    category = CostsCategory.objects.filter(id=id).first()
    return category.name
def getSpeciesName(input_str):
    id_str = input_str.split('(')[1].split(')')[0]
    id = int(id_str)
    species = Species.objects.filter(id=id).first()
    return species.name
def displayAnimalStatus(status):
    if status:
        return "Zdrowy"
    else:
        return "Chory"
def create_table(data, col_widths):
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return table   
def changeDateFormat(date):
    data_czas = datetime.fromisoformat(date)
    locale.setlocale(locale.LC_TIME, 'pl_PL.utf8')  # Ustawienie języka na polski
    nowy_format = data_czas.strftime('%d %B %Y')
    return nowy_format
def remove_diacritics(text):
    return unidecode(text)