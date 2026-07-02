# Módulo de exemplo. Duplique este diretório para cada componente real do sistema e registre o
# novo módulo em Arquitetura/mapa.yml na mesma branch/PR (guardrail de Arquitetura Viva).

# variable "nome_ambiente" {
#   type        = string
#   description = "Ambiente alvo (dev, homol, prod)."
# }

# Recurso de exemplo (comentado). Aplicar o princípio de menor privilégio em qualquer policy IAM
# (ver docs/steering/seguranca.md).
# resource "null_resource" "exemplo" {
#   triggers = {
#     ambiente = var.nome_ambiente
#   }
# }
