package com.soa.demo.account;

import java.math.BigDecimal;

public record MovimientoResponse(String numeroCuenta, String tipoMovimiento,
                                 BigDecimal monto, BigDecimal saldoResultante) { }
