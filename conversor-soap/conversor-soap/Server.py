from wsgiref.simple_server import make_server
from spyne import Application, rpc, ServiceBase, Double
from spyne.model.fault import Fault
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class ConversorService(ServiceBase):

    @rpc(Double, _returns=Double)
    def celsius_a_fahrenheit(ctx, celsius):
        if celsius < -273.15:
            raise Fault(
                faultcode="Client",
                faultstring="La temperatura no puede ser menor al cero absoluto (-273.15 °C)"
            )
        return (celsius * 9.0 / 5.0) + 32.0

    @rpc(Double, _returns=Double)
    def fahrenheit_a_celsius(ctx, fahrenheit):
        if fahrenheit < -459.67:
            raise Fault(
                faultcode="Client",
                faultstring="La temperatura no puede ser menor al cero absoluto (-459.67 °F)"
            )
        return (fahrenheit - 32.0) * 5.0 / 9.0

    @rpc(Double, _returns=Double)
    def kilometros_a_millas(ctx, kilometros):
        if kilometros < 0:
            raise Fault(
                faultcode="Client",
                faultstring="La distancia no puede ser negativa"
            )
        return kilometros * 0.621371


application = Application(
    [ConversorService],
    tns="http://ejemplo.com/conversor",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    server = make_server("127.0.0.1", 8000, wsgi_app)
    print("Servidor escuchando en http://127.0.0.1:8000")
    print("El WSDL esta disponible en http://127.0.0.1:8000/?wsdl")
    server.serve_forever()