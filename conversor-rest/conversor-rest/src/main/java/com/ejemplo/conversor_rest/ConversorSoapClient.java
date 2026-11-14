package com.ejemplo.conversor_rest;

import jakarta.xml.bind.JAXBElement;
import org.springframework.ws.client.core.support.WebServiceGatewaySupport;
import org.springframework.ws.soap.client.core.SoapActionCallback;
import com.ejemplo.conversor.wsdl.*;

public class ConversorSoapClient extends WebServiceGatewaySupport {

    private final ObjectFactory factory = new ObjectFactory();

    public Double celsiusAFahrenheit(Double celsius) {
        CelsiusAFahrenheit req = new CelsiusAFahrenheit();
        req.setCelsius(celsius);
        CelsiusAFahrenheitResponse res = call(factory.createCelsiusAFahrenheit(req), "celsius_a_fahrenheit");
        return res.getCelsiusAFahrenheitResult();
    }

    public Double fahrenheitACelsius(Double fahrenheit) {
        FahrenheitACelsius req = new FahrenheitACelsius();
        req.setFahrenheit(fahrenheit);
        FahrenheitACelsiusResponse res = call(factory.createFahrenheitACelsius(req), "fahrenheit_a_celsius");
        return res.getFahrenheitACelsiusResult();
    }

    public Double kilometrosAMillas(Double kilometros) {
        KilometrosAMillas req = new KilometrosAMillas();
        req.setKilometros(kilometros);
        KilometrosAMillasResponse res = call(factory.createKilometrosAMillas(req), "kilometros_a_millas");
        return res.getKilometrosAMillasResult();
    }

    @SuppressWarnings("unchecked")
    private <T> T call(JAXBElement<?> request, String soapAction) {
        JAXBElement<T> response = (JAXBElement<T>) getWebServiceTemplate()
                .marshalSendAndReceive(request, new SoapActionCallback(soapAction));
        return response.getValue();
    }
}