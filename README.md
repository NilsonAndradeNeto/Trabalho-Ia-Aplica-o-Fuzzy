
NPC Weapon Selection (Python)
=============================

Este projeto converte a modelagem fuzzy (original em .fcl / jFuzzyLogic) para Python usando scikit-fuzzy.
Ele foi gerado automaticamente para uso em apresentação acadêmica e contém:


- npc_fuzzy.py : script principal (entrada via terminal + gráficos)
- requirements.txt : dependências para instalar com pip
- README.md : este arquivo

Instruções rápidas:
1. Criar um ambiente virtual (opcional):
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows PowerShell

2. Instalar dependências:
   pip install -r requirements.txt

3. Rodar:
   python npc_fuzzy.py

Observações:
- As funções de pertinência e regras foram traduzidas a partir dos arquivos Pistola.fcl, Sniper.fcl e RocketLauncher.fcl 
