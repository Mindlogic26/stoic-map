from http.server import BaseHTTPRequestHandler
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from datetime import datetime
import json
import io

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        user_name = data.get('name', 'JOHN DOE').upper()
        dob_str = data.get('dob', '1995-01-01')
        
        # 1. Calculation Logic
        birth_date = datetime.strptime(dob_str, '%Y-%m-%d')
        now = datetime.now()
        years_lived = now.year - birth_date.year - ((now.month, now.day) < (birth_date.month, birth_date.day))
        last_birthday = birth_date.replace(year=now.year) if now >= birth_date.replace(year=now.year) else birth_date.replace(year=now.year - 1)
        weeks_this_year = (now - last_birthday).days // 7
        current_week_index = (years_lived * 52) + weeks_this_year

        # 2. PDF Setup
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A3)
        width, height = A3
        
        # 3. Headers
        c.setFont("Helvetica-Bold", 40)
        c.drawString(25*mm, height - 40*mm, "MEMENTO MORI")
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 25*mm, height - 35*mm, user_name)
        c.drawRightString(width - 25*mm, height - 40*mm, "ARCHIVAL MAP | 80 YEAR POTENTIAL")

        # 4. The 80-Year Grid
        startX, boxSize, padding, midGap, decadeGap = 25*mm, 3.0*mm, 1.0*mm, 8.0*mm, 5.5*mm
        currentY = height - 70*mm

        for y in range(1, 81):
            if y > 1 and (y-1) % 10 == 0: currentY -= decadeGap
            
            # Year Labels
            if y % 10 == 0 or y == 1:
                c.setFont("Helvetica-Bold", 8)
                c.drawRightString(startX - 5*mm, currentY + 1*mm, str(y))

            for w in range(1, 53):
                xOff = (w-1) * (boxSize + padding)
                if w > 26: xOff += midGap
                
                weekIdx = ((y-1) * 52) + (w-1)
                if weekIdx < current_week_index:
                    c.setFillColorRGB(0,0,0)
                    c.rect(startX + xOff, currentY, boxSize, boxSize, fill=1)
                elif weekIdx == current_week_index:
                    c.setFillColorRGB(1, 0.23, 0.23) # Stoic Red
                    c.rect(startX + xOff, currentY, boxSize, boxSize, fill=1)
                else:
                    c.setStrokeColorRGB(0,0,0)
                    c.rect(startX + xOff, currentY, boxSize, boxSize, fill=0)
            
            currentY -= (boxSize + padding)

        # 5. Footer Quotes
        c.setFillColorRGB(0,0,0)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(25*mm, 30*mm, '"It is not that we have a short time to live, but that we waste a lot of it."')
        c.drawString(25*mm, 25*mm, "— SENECA")
        c.drawRightString(width - 25*mm, 30*mm, '"Very little is needed to make a happy life; it is all within yourself."')
        c.drawRightString(width - 25*mm, 25*mm, "— MARCUS AURELIUS")

        c.showPage()
        c.save()

        # 6. Response
        self.send_response(200)
        self.send_header('Content-Type', 'application/pdf')
        self.send_header('Content-Disposition', 'attachment; filename="FORGE_MAP.pdf"')
        self.end_headers()
        self.wfile.write(buffer.getvalue())
