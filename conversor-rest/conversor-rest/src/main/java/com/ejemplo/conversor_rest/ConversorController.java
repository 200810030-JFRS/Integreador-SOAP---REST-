package com.ejemplo.conversor_rest;

import java.util.LinkedHashMap;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/conversor")
public class ConversorController {

    private final ConversorSoapClient soap;

    public ConversorController(ConversorSoapClient soap) {
        this.soap = soap;
    }

    @GetMapping("/celsius-a-fahrenheit")
    public Map<String, Object> celsiusAFahrenheit(@RequestParam Double valor) {
        return resultado("celsius-a-fahrenheit", valor, soap.celsiusAFahrenheit(valor));
    }

    @GetMapping("/fahrenheit-a-celsius")
    public Map<String, Object> fahrenheitACelsius(@RequestParam Double valor) {
        return resultado("fahrenheit-a-celsius", valor, soap.fahrenheitACelsius(valor));
    }

    @GetMapping("/kilometros-a-millas")
    public Map<String, Object> kilometrosAMillas(@RequestParam Double valor) {
        return resultado("kilometros-a-millas", valor, soap.kilometrosAMillas(valor));
    }

    private Map<String, Object> resultado(String conversion, Double valorRecibido, Double res) {
        Map<String, Object> json = new LinkedHashMap<>();
        json.put("conversion", conversion);
        json.put("valor", valorRecibido);
        json.put("resultado", res);
        return json;
    }
}