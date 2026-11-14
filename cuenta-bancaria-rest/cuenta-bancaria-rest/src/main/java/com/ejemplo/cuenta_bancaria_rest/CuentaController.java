package com.soa.demo.account;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/cuentas")
public class CuentaController {
    private final CuentaService service;
    public CuentaController(CuentaService service) { this.service = service; }

    @GetMapping("/{numeroCuenta}/saldo")
    public SaldoResponse consultarSaldo(@PathVariable String numeroCuenta) {
        return service.consultarSaldo(numeroCuenta);
    }

    @PostMapping("/{numeroCuenta}/depositos")
    public ResponseEntity<MovimientoResponse> depositar(@PathVariable String numeroCuenta,
                                                         @RequestBody MovimientoRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(service.depositar(numeroCuenta, request.monto()));
    }

    @PostMapping("/{numeroCuenta}/retiros")
    public MovimientoResponse retirar(@PathVariable String numeroCuenta,
                                      @RequestBody MovimientoRequest request) {
        return service.retirar(numeroCuenta, request.monto());
    }
}
