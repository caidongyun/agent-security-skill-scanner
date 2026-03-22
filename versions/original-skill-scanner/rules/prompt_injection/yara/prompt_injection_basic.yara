rule PromptInjection_Basic {
    meta:
        id = "PI-001"
        name = "Basic Prompt Injection Detection"
        severity = "high"
        description = "Detects basic prompt injection attempts"
    strings:
        $inj1 = "ignore previous instructions"
        $inj2 = "you are now"
        $inj3 = "new system prompt"
    condition:
        any of them
}
