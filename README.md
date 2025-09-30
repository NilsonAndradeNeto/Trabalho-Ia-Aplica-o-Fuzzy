
NPC Weapon Selection (Python)
=============================

Este projeto converte a modelagem fuzzy (original em .fcl / jFuzzyLogic) para Python usando scikit-fuzzy.
Ele foi gerado automaticamente para uso em apresentação acadêmica e contém:


- npc_fuzzy.py : script principal (entrada via terminal + gráficos)
- requirements.txt : dependências para instalar com pip
- README.md : este arquivo

Instruções rápidas:
1. Criar um ambiente virtual (opcional):
```bash
   python -m venv venv # ou python 3
```

2. Execute o ambiente virtual (opicional):
```bash
   source venv/bin/activate   # Linux / macOS
```
```bash
   venv\Scripts\activate    # Windows PowerShell
```
> (Linux/MacOS) -> Em caso de erro de permissão rode: `chmod u+r ./venv/bin/activate`
   
   
3. Instalar dependências:
   pip install -r requirements.txt
> Em caso de erro de versão da lib `scikit-fuzzy==0.8.0` modifique para `scikit-fuzzy==0.5.0`
> execute também: `pip install -U numpy scipy scikit-fuzzy matplotlib networkx`

5. Rodar:
   python npc_fuzzy.py

Observações:
- As funções de pertinência e regras foram traduzidas a partir dos arquivos Pistola.fcl, Sniper.fcl e RocketLauncher.fcl 
