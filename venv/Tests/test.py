from reportlab.pdfgen import canvas



def hello(c):

    c.drawImage("perrito.jpg", 0, 0, width=595, height=841)

    for x in range(10):
        c.drawString(100, 100+10*x, "Hello World")
    #canvas.drawImage(self, image, x, y, width=None, height=None, mask=None)

c = canvas.Canvas("hello.pdf")
hello(c)
c.showPage()
c.save()
