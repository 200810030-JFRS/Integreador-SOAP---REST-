from decimal import Decimal, InvalidOperation
from pathlib import Path
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn
from xml.etree import ElementTree as ET
from urllib.parse import parse_qs
import threading

SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
NAMESPACE = "urn:CuentaBancaria"
PUERTO = 8000

ET.register_namespace("soapenv", SOAP_NS)


class BusinessError(Exception):
    pass


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def decimal_value(raw, field_name):
    try:
        value = Decimal(str(raw).strip())
    except (InvalidOperation, ValueError, AttributeError):
        raise BusinessError(f"El campo {field_name} debe contener un numero decimal valido.")
    if not value.is_finite():
        raise BusinessError(f"El campo {field_name} debe contener un numero decimal finito.")
    return value


def xml_response(start_response, body, status="200 OK"):
    data = ET.tostring(body, encoding="utf-8", xml_declaration=True)
    start_response(status, [
        ("Content-Type", "text/xml; charset=utf-8"),
        ("Content-Length", str(len(data))),
        ("Cache-Control", "no-store"),
    ])
    return [data]


def soap_envelope(payload):
    envelope = ET.Element(f"{{{SOAP_NS}}}Envelope")
    body = ET.SubElement(envelope, f"{{{SOAP_NS}}}Body")
    body.append(payload)
    return envelope


def soap_fault(message):
    envelope = ET.Element(f"{{{SOAP_NS}}}Envelope")
    body = ET.SubElement(envelope, f"{{{SOAP_NS}}}Body")
    fault = ET.SubElement(body, f"{{{SOAP_NS}}}Fault")
    ET.SubElement(fault, "faultcode").text = "soapenv:Client"
    ET.SubElement(fault, "faultstring").text = str(message)
    return envelope


class SoapApplication:
    def __init__(self, namespace, wsdl_text, operations):
        self.namespace = namespace
        self.wsdl_text = wsdl_text.encode("utf-8")
        self.operations = operations

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")
        query = parse_qs(environ.get("QUERY_STRING", ""))

        if method == "GET" and ("wsdl" in query or path.lower().endswith(".wsdl") or path in ("/", "/wsdl")):
            data = self.wsdl_text
            start_response("200 OK", [
                ("Content-Type", "text/xml; charset=utf-8"),
                ("Content-Length", str(len(data))),
                ("Cache-Control", "no-store"),
            ])
            return [data]

        if method != "POST":
            message = b"Use GET /?wsdl para consultar el contrato o POST / para enviar una solicitud SOAP."
            start_response("405 Method Not Allowed", [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", str(len(message))),
            ])
            return [message]

        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
            raw = environ["wsgi.input"].read(length)
            root = ET.fromstring(raw)
            body = root.find(f"{{{SOAP_NS}}}Body")
            if body is None or len(body) == 0:
                raise BusinessError("La solicitud SOAP no contiene una operacion en el Body.")
            operation_element = list(body)[0]
            operation = local_name(operation_element.tag)
            if operation not in self.operations:
                raise BusinessError(f"La operacion {operation} no esta disponible en este servicio.")
            params = {local_name(child.tag): (child.text or "") for child in list(operation_element)}
            result = self.operations[operation](params)
            response = ET.Element(f"{{{self.namespace}}}{operation}Response")
            ET.SubElement(response, f"{{{self.namespace}}}{operation}Result").text = format(result, "f")
            return xml_response(start_response, soap_envelope(response), "200 OK")
        except BusinessError as exc:
            return xml_response(start_response, soap_fault(str(exc)), "500 Internal Server Error")
        except ET.ParseError:
            return xml_response(start_response, soap_fault("El mensaje SOAP no contiene XML valido."), "400 Bad Request")
        except Exception:
            return xml_response(start_response, soap_fault("No fue posible procesar la solicitud SOAP."), "500 Internal Server Error")


def run(app, port):
    host = "0.0.0.0"
    print(f"Servicio SOAP iniciado en http://localhost:{port}/")
    print(f"Contrato WSDL: http://localhost:{port}/?wsdl")
    print("Presiona Ctrl+C para detener el servicio.")
    with make_server(host, port, app, server_class=ThreadingWSGIServer) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServicio SOAP detenido.")


WSDL_CUENTA_BANCARIA = f"""<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="{NAMESPACE}"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="{NAMESPACE}"
             name="CuentaBancaria">
    <types>
        <xsd:schema targetNamespace="{NAMESPACE}" elementFormDefault="qualified">
            <xsd:element name="ConsultarSaldo">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="numeroCuenta" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="ConsultarSaldoResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="ConsultarSaldoResult" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="Depositar">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="numeroCuenta" type="xsd:string"/>
                        <xsd:element name="monto" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="DepositarResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="DepositarResult" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="Retirar">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="numeroCuenta" type="xsd:string"/>
                        <xsd:element name="monto" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            <xsd:element name="RetirarResponse">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="RetirarResult" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>

    <message name="ConsultarSaldoRequest">
        <part name="parameters" element="tns:ConsultarSaldo"/>
    </message>
    <message name="ConsultarSaldoResponse">
        <part name="parameters" element="tns:ConsultarSaldoResponse"/>
    </message>
    <message name="DepositarRequest">
        <part name="parameters" element="tns:Depositar"/>
    </message>
    <message name="DepositarResponse">
        <part name="parameters" element="tns:DepositarResponse"/>
    </message>
    <message name="RetirarRequest">
        <part name="parameters" element="tns:Retirar"/>
    </message>
    <message name="RetirarResponse">
        <part name="parameters" element="tns:RetirarResponse"/>
    </message>

    <portType name="CuentaBancariaPortType">
        <operation name="ConsultarSaldo">
            <input message="tns:ConsultarSaldoRequest"/>
            <output message="tns:ConsultarSaldoResponse"/>
        </operation>
        <operation name="Depositar">
            <input message="tns:DepositarRequest"/>
            <output message="tns:DepositarResponse"/>
        </operation>
        <operation name="Retirar">
            <input message="tns:RetirarRequest"/>
            <output message="tns:RetirarResponse"/>
        </operation>
    </portType>

    <binding name="CuentaBancariaBinding" type="tns:CuentaBancariaPortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="ConsultarSaldo">
            <soap:operation soapAction="urn:CuentaBancaria#ConsultarSaldo"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
        <operation name="Depositar">
            <soap:operation soapAction="urn:CuentaBancaria#Depositar"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
        <operation name="Retirar">
            <soap:operation soapAction="urn:CuentaBancaria#Retirar"/>
            <input><soap:body use="literal"/></input>
            <output><soap:body use="literal"/></output>
        </operation>
    </binding>

    <service name="CuentaBancariaService">
        <port name="CuentaBancariaPort" binding="tns:CuentaBancariaBinding">
            <soap:address location="http://localhost:{PUERTO}/"/>
        </port>
    </service>
</definitions>
"""

CUENTAS = {
    "001": Decimal("1000.00"),
    "002": Decimal("250.00"),
}
LOCK = threading.Lock()


def obtener_cuenta(params):
    numero = str(params.get("numeroCuenta", "")).strip()
    if not numero:
        raise BusinessError("El numero de cuenta es obligatorio.")
    if numero not in CUENTAS:
        raise BusinessError(f"La cuenta {numero} no existe.")
    return numero


def consultar_saldo(params):
    with LOCK:
        numero = obtener_cuenta(params)
        return CUENTAS[numero].quantize(Decimal("0.01"))


def depositar(params):
    with LOCK:
        numero = obtener_cuenta(params)
        monto = decimal_value(params.get("monto"), "monto")
        if monto <= Decimal("0"):
            raise BusinessError("El monto del deposito debe ser mayor que cero.")
        CUENTAS[numero] = (CUENTAS[numero] + monto).quantize(Decimal("0.01"))
        return CUENTAS[numero]


def retirar(params):
    with LOCK:
        numero = obtener_cuenta(params)
        monto = decimal_value(params.get("monto"), "monto")
        if monto <= Decimal("0"):
            raise BusinessError("El monto del retiro debe ser mayor que cero.")
        if monto > CUENTAS[numero]:
            raise BusinessError("Saldo insuficiente para realizar el retiro.")
        CUENTAS[numero] = (CUENTAS[numero] - monto).quantize(Decimal("0.01"))
        return CUENTAS[numero]


if __name__ == "__main__":
    operaciones = {
        "ConsultarSaldo": consultar_saldo,
        "Depositar": depositar,
        "Retirar": retirar,
    }
    app = SoapApplication(NAMESPACE, WSDL_CUENTA_BANCARIA, operaciones)
    run(app, PUERTO)