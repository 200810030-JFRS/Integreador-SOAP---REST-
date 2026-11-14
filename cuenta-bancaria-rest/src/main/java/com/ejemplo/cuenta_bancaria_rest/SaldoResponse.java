package com.soa.demo.account;

import java.math.BigDecimal;

public record SaldoResponse(String numeroCuenta, BigDecimal saldo) { }
