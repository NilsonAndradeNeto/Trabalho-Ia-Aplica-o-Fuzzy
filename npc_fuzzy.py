#!/usr/bin/env python3
"""
npc_fuzzy.py - Versão polida com rótulos claros por arma
- Entrada: distancia (0-100), municao (0-100)
- Saída: desejabilidade por arma (0-100)
- Gera dashboard de gráficos organizado, identifica cada plot e salva em ./output/
"""

import os
import time
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# --- Universos ---
x_dist = np.arange(0, 101, 1)
x_mun = np.arange(0, 101, 1)
x_des = np.arange(0, 101, 1)

# --- Variáveis fuzzy (entradas) ---
distancia = ctrl.Antecedent(x_dist, 'distancia')
municao = ctrl.Antecedent(x_mun, 'municao')

# --- Variável de saída ---
desejabilidade = ctrl.Consequent(x_des, 'desejabilidade')

# --- Funções de pertinência (baseadas nos .fcl originais) ---
# Distância
distancia['perto']  = fuzz.trimf(distancia.universe, [0, 0, 35])
distancia['medio']  = fuzz.trimf(distancia.universe, [20, 50, 80])
distancia['longe']  = fuzz.trimf(distancia.universe, [60, 100, 100])

# Munição
municao['baixa'] = fuzz.trimf(municao.universe, [0, 0, 40])
municao['media'] = fuzz.trimf(municao.universe, [20, 50, 80])
municao['alta']  = fuzz.trimf(municao.universe, [60, 100, 100])

# Saída desejabilidade
desejabilidade['indesejavel']    = fuzz.trimf(desejabilidade.universe, [0, 0, 40])
desejabilidade['desejavel']      = fuzz.trimf(desejabilidade.universe, [30, 55, 75])
desejabilidade['imprescindivel'] = fuzz.trimf(desejabilidade.universe, [65, 85, 100])

# ---------------- Regras (cada arma) ----------------
# Pistola (melhor em curto alcance)
p_rules = [
    ctrl.Rule(distancia['perto'] & municao['alta'], desejabilidade['imprescindivel']),
    ctrl.Rule(distancia['perto'] & municao['media'], desejabilidade['desejavel']),
    ctrl.Rule(distancia['perto'] & municao['baixa'], desejabilidade['indesejavel']),
    ctrl.Rule(distancia['medio'] & municao['media'], desejabilidade['desejavel']),
    ctrl.Rule(distancia['medio'] & municao['alta'], desejabilidade['desejavel']),
    ctrl.Rule(distancia['longe'], desejabilidade['indesejavel']),
]
p_ctrl = ctrl.ControlSystem(p_rules)

# Sniper (melhor em longa)
s_rules = [
    ctrl.Rule(distancia['longe'] & municao['alta'], desejabilidade['imprescindivel']),
    ctrl.Rule(distancia['longe'] & municao['media'], desejabilidade['desejavel']),
    ctrl.Rule(distancia['medio'] & (municao['media'] | municao['alta']), desejabilidade['desejavel']),
    ctrl.Rule(distancia['perto'], desejabilidade['indesejavel']),
]
s_ctrl = ctrl.ControlSystem(s_rules)

# Rocket Launcher (bom em medio/longe se munição disponível)
r_rules = [
    ctrl.Rule(distancia['perto'], desejabilidade['indesejavel']),
    ctrl.Rule(distancia['medio'] & municao['alta'], desejabilidade['imprescindivel']),
    ctrl.Rule(distancia['medio'] & municao['media'], desejabilidade['desejavel']),
    ctrl.Rule(distancia['longe'] & ~municao['baixa'], desejabilidade['desejavel']),
    ctrl.Rule(distancia['longe'] & municao['alta'], desejabilidade['imprescindivel']),
]
r_ctrl = ctrl.ControlSystem(r_rules)

# ---------------- Função utilitária: interp membership ----------------
def degree_of(term_mf, universe, value):
    """Interpreta o grau de pertinência de uma mf (array) no point value."""
    return fuzz.interp_membership(universe, term_mf, value)

# ---------------- Avaliar (cria simulações novas cada vez) ----------------
def avaliar(dist_val, mun_val):
    p_sim = ctrl.ControlSystemSimulation(p_ctrl)
    s_sim = ctrl.ControlSystemSimulation(s_ctrl)
    r_sim = ctrl.ControlSystemSimulation(r_ctrl)

    p_sim.input['distancia'] = dist_val
    p_sim.input['municao'] = mun_val
    p_sim.compute()
    val_p = float(p_sim.output.get('desejabilidade', 0))

    s_sim.input['distancia'] = dist_val
    s_sim.input['municao'] = mun_val
    s_sim.compute()
    val_s = float(s_sim.output.get('desejabilidade', 0))

    r_sim.input['distancia'] = dist_val
    r_sim.input['municao'] = mun_val
    r_sim.compute()
    val_r = float(r_sim.output.get('desejabilidade', 0))

    # Também retornamos os sims para plot com shading/defuzz
    return {
        'Pistola': {'value': val_p, 'sim': p_sim},
        'Sniper': {'value': val_s, 'sim': s_sim},
        'Rocket Launcher': {'value': val_r, 'sim': r_sim}
    }

# ---------------- Plotagem organizada e profissional (com rótulos grandes) ----------------
def plot_results(dist_val, mun_val, results):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    fname = os.path.join(out_dir, f"result_{timestamp}.png")

    # Layout: 2 rows x 3 cols
    fig = plt.figure(constrained_layout=True, figsize=(15, 9))
    gs = fig.add_gridspec(2, 3)

    # Top row: entradas (distancia, municao) + resumo (texto)
    ax_dist = fig.add_subplot(gs[0, 0])
    ax_mun  = fig.add_subplot(gs[0, 1])
    ax_text = fig.add_subplot(gs[0, 2])
    ax_text.axis('off')

    # Bottom row: outputs por arma (3 plots)
    ax_p = fig.add_subplot(gs[1, 0])
    ax_s = fig.add_subplot(gs[1, 1])
    ax_r = fig.add_subplot(gs[1, 2])

    # --- Plot de entradas (com MFs) ---
    # Distancia MFs
    ax_dist.plot(distancia.universe, distancia['perto'].mf, linestyle='-', label='perto')
    ax_dist.plot(distancia.universe, distancia['medio'].mf, linestyle='-', label='medio')
    ax_dist.plot(distancia.universe, distancia['longe'].mf, linestyle='-', label='longe')
    ax_dist.set_title(f"Distância (valor = {dist_val})")
    ax_dist.set_xlabel("Distância")
    ax_dist.set_ylabel("Grau de pertinência")
    ax_dist.set_xlim(0, 100)
    ax_dist.legend()
    ax_dist.axvline(dist_val, color='gray', linestyle='--', linewidth=1)
    d_perto = degree_of(distancia['perto'].mf, distancia.universe, dist_val)
    d_medio = degree_of(distancia['medio'].mf, distancia.universe, dist_val)
    d_longe = degree_of(distancia['longe'].mf, distancia.universe, dist_val)
    ax_dist.plot([dist_val]*3, [d_perto, d_medio, d_longe], 'o', markersize=6)
    ax_dist.text(0.02, 0.95, f"perto={d_perto:.2f}\nmedio={d_medio:.2f}\nlonge={d_longe:.2f}",
                 transform=ax_dist.transAxes, fontsize=9, verticalalignment='top',
                 bbox=dict(boxstyle="round", fc="wheat", alpha=0.6))

    # Munição MFs
    ax_mun.plot(municao.universe, municao['baixa'].mf, linestyle='-', label='baixa')
    ax_mun.plot(municao.universe, municao['media'].mf, linestyle='-', label='media')
    ax_mun.plot(municao.universe, municao['alta'].mf, linestyle='-', label='alta')
    ax_mun.set_title(f"Munição (valor = {mun_val})")
    ax_mun.set_xlabel("Munição")
    ax_mun.set_ylabel("Grau de pertinência")
    ax_mun.set_xlim(0, 100)
    ax_mun.legend()
    ax_mun.axvline(mun_val, color='gray', linestyle='--', linewidth=1)
    m_baixa = degree_of(municao['baixa'].mf, municao.universe, mun_val)
    m_media = degree_of(municao['media'].mf, municao.universe, mun_val)
    m_alta  = degree_of(municao['alta'].mf, municao.universe, mun_val)
    ax_mun.plot([mun_val]*3, [m_baixa, m_media, m_alta], 'o', markersize=6)
    ax_mun.text(0.02, 0.95, f"baixa={m_baixa:.2f}\nmedia={m_media:.2f}\nalta={m_alta:.2f}",
                transform=ax_mun.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle="round", fc="wheat", alpha=0.6))

    # --- Resumo textual (lado direito, top) ---
    values_text = ""
    for name, info in results.items():
        values_text += f"{name}: {info['value']:.2f}\n"
    best_name = max(results, key=lambda k: results[k]['value'])
    best_val = results[best_name]['value']
    values_text += "\nRecomendado:\n" + f"{best_name} ({best_val:.2f})"
    ax_text.text(0.02, 0.95, values_text, fontsize=12, verticalalignment='top',
                 bbox=dict(boxstyle="round", fc="lightcyan", alpha=0.9))

    # --- Função auxiliar para plot de saída com marcação da defuzz e label grande ---
    def plot_output_labeled(ax, sim, title, big_label):
        # desenha a agregação + defuzz
        desejabilidade.view(sim=sim, ax=ax)
        ax.set_title(title)
        # marca a defuzz (valor numérico)
        val = float(sim.output.get('desejabilidade', 0.0))
        ax.axvline(val, color='k', linestyle='--', linewidth=1.2)
        ax.text(val, 0.05, f" {val:.2f}", rotation=90, verticalalignment='bottom')
        # big label (identificador claro da arma)
        ax.text(0.5, 0.85, big_label, transform=ax.transAxes,
                fontsize=16, fontweight='bold', ha='center',
                bbox=dict(boxstyle="round", fc="white", alpha=0.8))

    # Plot Pistola
    plot_output_labeled(ax_p, results['Pistola']['sim'], "Pistola (desejabilidade)", "PISTOLA")

    # Plot Sniper
    plot_output_labeled(ax_s, results['Sniper']['sim'], "Sniper (desejabilidade)", "SNIPER")

    # Plot Rocket
    plot_output_labeled(ax_r, results['Rocket Launcher']['sim'], "Rocket Launcher (desejabilidade)", "ROCKET LAUNCHER")

    # Salvar figura e mostrar
    fig.suptitle(f"NPC Weapon Selection - distancia={dist_val}, municao={mun_val}", fontsize=14)
    fig.savefig(fname, dpi=160)
    try:
        plt.show()
    except Exception:
        # Em caso de ambiente headless, apenas informe o local do arquivo
        print(f"(Headless) Gráfico salvo em: {fname}")

    print(f"Gráfico final salvo em: {fname}")

# ---------------- Main ----------------
def main():
    print("Weapon Selection - versão Python\n")
    try:
        d = float(input("Informe a distância do inimigo (0-100): "))
        m = float(input("Informe a quantidade de munição (0-100): "))
    except Exception as e:
        print("Entrada inválida. Use números entre 0 e 100.", e)
        return

    # validar faixa
    if not (0 <= d <= 100 and 0 <= m <= 100):
        print("Os valores devem estar entre 0 e 100.")
        return

    results = avaliar(d, m)

    print("\n=== Resultados Fuzzy ===")
    for name, info in results.items():
        print(f"{name} -> desejabilidade = {info['value']:.2f}")

    best = max(results, key=lambda k: results[k]['value'])
    print(f"\n>>> Arma Recomendada: {best} (valor = {results[best]['value']:.2f})")

    plot_results(d, m, results)

if __name__ == "__main__":
    main()
cl