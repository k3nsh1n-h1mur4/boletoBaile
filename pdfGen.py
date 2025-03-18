from fpdf import FPDF
from pathlib import Path


class FPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.path = Path.cwd().joinpath('boletoBaile')
        self.pathStatic = self.path.joinpath('static')
        
    def Image(self):
        self.image(self.pathStatic.joinpath('BOLETO_QR.png'), x=10, y=10, w=100, h=150)
