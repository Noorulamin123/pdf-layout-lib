from reportlab.platypus import Flowable
from reportlab.lib import colors

class Separator(Flowable):
    def __init__(
        self,
        length=500,
        thickness=1,
        color=colors.black,
        direction="horizontal",
        margin_before=10,
        margin_after=10,
        dash=None,
    ):
        super().__init__()
        self.length = length
        self.thickness = thickness
        self.color = color
        self.direction = direction.lower()
        self.margin_before = margin_before
        self.margin_after = margin_after
        self.dash = dash

        if self.direction == "horizontal":
            self.width = self.length
            self.height = self.margin_before + self.thickness + self.margin_after
        elif self.direction == "vertical":
            self.width = self.margin_before + self.thickness + self.margin_after
            self.height = self.length
        else:
            raise ValueError(f"Unsupported direction: {direction}")

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)

        if self.dash and isinstance(self.dash, (list, tuple)):
            c.setDash(self.dash)
        else:
            c.setDash()

        if self.direction == "horizontal":
            y = self.margin_after + self.thickness / 2
            c.line(0, y, self.length, y)
        else:
            x = self.margin_before + self.thickness / 2
            c.line(x, 0, x, self.length)

        c.restoreState()

    def wrap(self, availWidth, availHeight):
        return self.width, self.height