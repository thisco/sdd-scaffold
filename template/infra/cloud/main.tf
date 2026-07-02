# Composição raiz da infraestrutura de nuvem.
# Cada componente lógico do sistema vira uma chamada de módulo em infra/cloud/modules/ e deve ter
# a entrada correspondente em Arquitetura/mapa.yml (avatar `tofu_modulo`).

module "exemplo_servico" {
  source = "./modules/exemplo-servico"

  # nome_ambiente = var.ambiente
}
