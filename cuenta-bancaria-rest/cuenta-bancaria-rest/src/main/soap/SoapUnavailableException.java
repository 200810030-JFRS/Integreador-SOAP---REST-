package com.ejemplo.cuenta_bancaria_rest.soap;

public class SoapUnavailableException extends RuntimeException {
    public SoapUnavailableException() {
        super("El servicio SOAP no esta disponible.");
    }
}
