terraform {
  required_version = ">= 1.8.0"

  # Descomente e configure o backend remoto de estado para este projeto.
  # backend "s3" {
  #   bucket = "<bucket-de-estado>"
  #   key    = "<projeto>/terraform.tfstate"
  #   region = "<regiao>"
  # }

  # required_providers {
  #   aws = {
  #     source  = "hashicorp/aws"
  #     version = "~> 5.0"
  #   }
  # }
}
