from reportlab.pdfgen import canvas



def hello(c):

    c.drawImage("TemplatePDF_3.png", 0, 0, width=580, height=830)

    for x in range(10):
        c.drawString(20, 620-20*x, "CTC-1"+str(x))
        c.drawString(90, 620-20*x, "Concepto"+str(x))
        c.drawString(200, 620-20*x, "PZA"+str(x))
        c.drawString(250, 620-20*x, "$1,000.00")

c = canvas.Canvas("PDF_Prueba.pdf")
hello(c)
c.showPage()
c.save()
