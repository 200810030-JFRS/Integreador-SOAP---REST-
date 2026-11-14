package com.soa.demo.account;

import com.soa.demo.soap.SoapGateway;
import java.math.BigDecimal;
import org.springframework.stereotype.Service;

@Service
public class CuentaService {
    private final SoapGateway soap;
    public CuentaService(SoapGateway soap) { this.soap = soap; }

    public SaldoResponse consultarSaldo(String numeroCuenta) {
        return new SaldoResponse(numeroCuenta, soap.invoke("ConsultarSaldo", numeroCuenta));
    }
    public MovimientoResponse depositar(String numeroCuenta, BigDecimal monto) {
        BigDecimal saldo = soap.invoke("Depositar", numeroCuenta, monto);
        return new MovimientoResponse(numeroCuenta, "DEPOSITO", monto, saldo);
    }
    public MovimientoResponse retirar(String numeroCuenta, BigDecimal monto) {
        BigDecimal saldo = soap.invoke("Retirar", numeroCuenta, monto);
        return new MovimientoResponse(numeroCuenta, "RETIRO", monto, saldo);
    }
}