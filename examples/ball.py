class Ball(object):

    def __init__(self, draw, x, y, radius):
        self.draw = draw
        self.x = x
        self.y = y
        self.radius = radius

        self.render()

    def render(self):
        self.draw.arc([(self.x-self.radius,self.y-self.radius),(self.x+self.radius,self.y+self.radius)], 0, 360, fill="BLUE")