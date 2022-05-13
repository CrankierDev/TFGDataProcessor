import db
from sqlalchemy import Column, String, Integer, Float


class AeroData(db.Base):
    __tablename__ = "logsData"

    id = Column(Integer, primary_key=True)
    method = Column(String(20), nullable=False)
    simulation = Column(String(20), nullable=False)
    angleOfAttack = Column(String(20), nullable=False)
    urlData = Column(String(300), nullable=False)
    momentsCoeff = Column(Float, nullable=False)
    dragCoeff = Column(Float, nullable=False)
    liftCoeff = Column(Float, nullable=False)
    yPlus = Column(Float, nullable=False)
    efficiency = Column(Float, nullable=False)

    def __init__(self, method, simulation, angleOfAttack, urlData, momentsCoeff, dragCoeff, liftCoeff, yPlus):
        self.method = method
        self.simulation = simulation
        self.angleOfAttack = angleOfAttack
        self.urlData = urlData
        self.momentsCoeff = momentsCoeff
        self.dragCoeff = dragCoeff
        self.liftCoeff = liftCoeff
        self.yPlus = yPlus
        self.efficiency = round((liftCoeff/dragCoeff), 3)

    def __repr__(self):
        return """Data log number {}: AOA {} from {}/{}."""\
                .format(self.id, self.angleOfAttack, self.method, self.simulation)

    def __str__(self):
        return """Data log number {}: AOA {} from {}/{}."""\
                .format(self.id, self.angleOfAttack, self.method, self.simulation)
