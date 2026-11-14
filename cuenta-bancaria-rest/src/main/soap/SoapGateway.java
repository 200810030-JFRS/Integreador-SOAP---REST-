package com.ejemplo.cuenta_bancaria_rest.soap;

import java.math.BigDecimal;
import java.net.URL;
import jakarta.xml.ws.soap.SOAPFaultException;
import org.apache.cxf.binding.soap.SoapFault;
import org.apache.cxf.endpoint.Client;
import org.apache.cxf.jaxws.endpoint.dynamic.JaxWsDynamicClientFactory;
import org.apache.cxf.transport.http.HTTPConduit;
import org.apache.cxf.transports.http.configuration.HTTPClientPolicy;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class SoapGateway {
    private final String endpoint;
    private Client client;

    public SoapGateway(@Value("${soap.endpoint}") String endpoint) {
        this.endpoint = endpoint;
    }

    public synchronized BigDecimal invoke(String operation, Object... parameters) {
        try {
            if (client == null) {
                client = createClientFromWsdl();
            }
            Object[] response = client.invoke(operation, parameters);
            if (response == null || response.length == 0 || response[0] == null) {
                throw new SoapUnavailableException();
            }
            Object value = response[0];
            if (value instanceof BigDecimal decimal) return decimal;
            return new BigDecimal(value.toString());
        } catch (SoapBusinessException | SoapUnavailableException ex) {
            throw ex;
        } catch (Exception ex) {
            String fault = findSoapFault(ex);
            if (fault != null && !fault.isBlank()) {
                throw new SoapBusinessException(fault);
            }
            client = null;
            throw new SoapUnavailableException();
        }
    }

    private Client createClientFromWsdl() throws Exception {
        URL wsdl = getClass().getResource("/wsdl/cuenta_bancaria.wsdl");
        if (wsdl == null) throw new IllegalStateException("No se encontro el WSDL incluido en resources.");
        Client created = JaxWsDynamicClientFactory.newInstance().createClient(wsdl.toExternalForm());
        created.getEndpoint().getEndpointInfo().setAddress(endpoint);
        if (created.getConduit() instanceof HTTPConduit conduit) {
            HTTPClientPolicy policy = new HTTPClientPolicy();
            policy.setConnectionTimeout(3000);
            policy.setReceiveTimeout(5000);
            conduit.setClient(policy);
        }
        return created;
    }

    private String findSoapFault(Throwable error) {
        Throwable current = error;
        while (current != null) {
            if (current instanceof SoapFault soapFault && soapFault.getMessage() != null) {
                return soapFault.getMessage();
            }
            if (current instanceof SOAPFaultException soapFault && soapFault.getFault() != null) {
                return soapFault.getFault().getFaultString();
            }
            current = current.getCause();
        }
        return null;
    }
}
