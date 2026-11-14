package com.ejemplo.conversor_rest;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.oxm.jaxb.Jaxb2Marshaller;

@Configuration
public class SoapConfig {

    @Value("${conversor.soap.url}")
    private String soapUrl;

    @Bean
    public Jaxb2Marshaller marshaller() {
        Jaxb2Marshaller marshaller = new Jaxb2Marshaller();
        marshaller.setContextPath("com.ejemplo.conversor.wsdl");
        return marshaller;
    }

    @Bean
    public ConversorSoapClient conversorSoapClient(Jaxb2Marshaller marshaller) {
        ConversorSoapClient client = new ConversorSoapClient();
        client.setDefaultUri(soapUrl);
        client.setMarshaller(marshaller);
        client.setUnmarshaller(marshaller);
        return client;
    }
}