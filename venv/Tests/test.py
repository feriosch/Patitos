from reportlab.pdfgen import canvas



def generarPDF(c):

    c.drawImage("TemplatePDF_3.png", 0, 0, width=580, height=830)

    c.drawString(77, 723,"Sucursal ejemplo")
    c.drawString(77, 668,"Fecha ejemplo")
    for x in range(10):
        c.drawString(20, 610-20*x, "CTC-"+str(x))
        c.drawString(77, 610-20*x, "Concepto"+str(x))
        c.drawString(350, 610-20*x, "PZA"+str(x))
        c.drawString(400, 610-20*x, str(x))
        c.drawString(445, 610-20*x, "$10.00")
        c.drawString(497, 610-20*x, "$1,000.00")

    c.showPage()

    c.drawImage("TemplatePDF_Croquis1.0.png", 0, 0, width=580, height=830)

    for x in range(5):
        c.drawString(33, 710 - 15 * x, "CTC-00" + str(x))
        c.drawString(93, 710 - 15 * x, "Concepto djklshflisdhfjesidhfbledhgfbolsdhbgfoidshbgvfiuk" + str(x))

        c.drawString(33, 600 - 20 * x, "CTC-" + str(x))
        c.drawString(120, 600 - 20 * x, "Concepto" + str(x))
        c.drawString(270, 600 - 20 * x, str(x)+" cm")
        c.drawString(325, 600 - 20 * x, str(x)+" cm")
        c.drawString(375, 600 - 20 * x, str(x)+" cm")
        c.drawString(420, 600 - 20 * x, str(x))
        c.drawString(480, 600 - 20 * x, "$1,000.00")
    c.drawImage("ositocroquis.jpg", 33, 90, width=500, height=360)
    c.drawString(490, 65, "$5,000")

    c.showPage()

    c.drawImage("TemplatePDF_Croquis1.0.png", 0, 0, width=580, height=830)

    for x in range(5):
        c.drawString(33, 710 - 15 * x, "CTC-00" + str(x))
        c.drawString(93, 710 - 15 * x, "Concepto djklshflisdhfjesidhfbledhgfbolsdhbgfoidshbgvfiuk" + str(x))

        c.drawString(33, 600 - 20 * x, "CTC-" + str(x))
        c.drawString(120, 600 - 20 * x, "Concepto" + str(x))
        c.drawString(270, 600 - 20 * x, str(x) + " cm")
        c.drawString(325, 600 - 20 * x, str(x) + " cm")
        c.drawString(375, 600 - 20 * x, str(x) + " cm")
        c.drawString(420, 600 - 20 * x, str(x))
        c.drawString(480, 600 - 20 * x, "$1,000.00")
    c.drawImage("monaschinas.jpg", 33, 90, width=500, height=360)
    c.drawString(490, 65, "$5,000")

    c.showPage()

    c.drawImage("whatsapp_ejemplo.png", 20, 20, width=550, height=800)

    c.showPage()

    c.drawImage("solicitud_de_empleo.png", 20, 20, width=550, height=800)




c = canvas.Canvas("PDF_Prueba.pdf")
generarPDF(c)
c.showPage()
c.save()
