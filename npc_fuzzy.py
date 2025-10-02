#!/usr/bin/env python3
import warnings
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

warnings.filterwarnings("ignore")


class NPCFuzzyWeaponSelector:
    def __init__(self) -> None:
        self._setup_universes()
        self._setup_memberships()
        self._setup_weapons()

    def _setup_universes(self) -> None:
        step = 1
        self.x_dist = np.arange(0, 101, step)
        self.x_mun = np.arange(0, 101, step)
        self.x_des = np.arange(0, 101, step)

    def _setup_memberships(self) -> None:
        self.distancia = ctrl.Antecedent(self.x_dist, "distancia")
        self.municao = ctrl.Antecedent(self.x_mun, "municao")
        self.desejabilidade = ctrl.Consequent(self.x_des, "desejabilidade")

        # Distância
        self.distancia["perto"] = fuzz.trimf(
            self.distancia.universe, [0, 0, 35]
        )
        self.distancia["medio"] = fuzz.trimf(
            self.distancia.universe, [20, 50, 80]
        )
        self.distancia["longe"] = fuzz.trimf(
            self.distancia.universe, [60, 100, 100]
        )

        # Munição
        self.municao["baixa"] = fuzz.trimf(
            self.municao.universe, [0, 0, 40]
        )
        self.municao["media"] = fuzz.trimf(
            self.municao.universe, [20, 50, 80]
        )
        self.municao["alta"] = fuzz.trimf(
            self.municao.universe, [60, 100, 100]
        )

        # Desejabilidade
        self.desejabilidade["indesejavel"] = fuzz.trimf(
            self.desejabilidade.universe, [0, 0, 40]
        )
        self.desejabilidade["desejavel"] = fuzz.trimf(
            self.desejabilidade.universe, [30, 55, 75]
        )
        self.desejabilidade["imprescindivel"] = fuzz.trimf(
            self.desejabilidade.universe, [65, 85, 100]
        )

    def _setup_weapons(self) -> None:
        self._weapon_catalog = [
            {
                "name": "Rocket Launcher",
                "color": "#d32f2f",
                "ammo_capacity": 3,
                "system": ctrl.ControlSystem(
                    [
                        # Curto alcance é inseguro para foguetes
                        ctrl.Rule(
                            self.distancia["perto"], self.desejabilidade["indesejavel"]
                        ),
                        # Alcance médio
                        ctrl.Rule(
                            self.distancia["medio"] & self.municao["alta"],
                            self.desejabilidade["imprescindivel"],
                        ),
                        ctrl.Rule(
                            self.distancia["medio"] & self.municao["media"],
                            self.desejabilidade["desejavel"],
                        ),
                        ctrl.Rule(
                            self.distancia["medio"] & self.municao["baixa"],
                            self.desejabilidade["indesejavel"],
                        ),
                        # Alcance longo
                        ctrl.Rule(
                            self.distancia["longe"] & self.municao["alta"],
                            self.desejabilidade["imprescindivel"],
                        ),
                        ctrl.Rule(
                            self.distancia["longe"] & self.municao["media"],
                            self.desejabilidade["desejavel"],
                        ),
                        ctrl.Rule(
                            self.distancia["longe"] & self.municao["baixa"],
                            self.desejabilidade["indesejavel"],
                        ),
                    ]
                ),
            },
            {
                "name": "Sniper Rifle",
                "color": "#fbc02d",
                "ammo_capacity": 10,
                "system": ctrl.ControlSystem(
                    [
                        # Ineficiente em curta distância
                        ctrl.Rule(
                            self.distancia["perto"], self.desejabilidade["indesejavel"]
                        ),
                        # Distância média
                        ctrl.Rule(
                            self.distancia["medio"]
                            & (self.municao["alta"] | self.municao["media"]),
                            self.desejabilidade["desejavel"],
                        ),
                        ctrl.Rule(
                            self.distancia["medio"] & self.municao["baixa"],
                            self.desejabilidade["indesejavel"],
                        ),
                        # Distância longa
                        ctrl.Rule(
                            self.distancia["longe"] & self.municao["alta"],
                            self.desejabilidade["imprescindivel"],
                        ),
                        ctrl.Rule(
                            self.distancia["longe"] & self.municao["media"],
                            self.desejabilidade["desejavel"],
                        ),
                        ctrl.Rule(
                            self.distancia["longe"] & self.municao["baixa"],
                            self.desejabilidade["desejavel"],
                        ),
                    ]
                ),
            },
            {
                "name": "Pistol",
                "color": "#388e3c",
                "ammo_capacity": 30,
                "system": ctrl.ControlSystem(
                    [
                        # Curto alcance
                        ctrl.Rule(
                            self.distancia["perto"] & self.municao["alta"],
                            self.desejabilidade["imprescindivel"],
                        ),
                        ctrl.Rule(
                            self.distancia["perto"] & self.municao["media"],
                            self.desejabilidade["desejavel"],
                        ),
                        ctrl.Rule(
                            self.distancia["perto"] & self.municao["baixa"],
                            self.desejabilidade["desejavel"],
                        ),
                        # Distância média
                        ctrl.Rule(
                            self.distancia["medio"] & self.municao["baixa"],
                            self.desejabilidade["desejavel"],
                        ),
                        ctrl.Rule(
                            self.distancia["medio"]
                            & (self.municao["media"] | self.municao["alta"]),
                            self.desejabilidade["desejavel"],
                        ),
                        # Longo alcance
                        ctrl.Rule(
                            self.distancia["longe"], self.desejabilidade["indesejavel"]
                        ),
                    ]
                ),
            },
        ]
    def evaluate(
        self,
        distancia_val: float,
        municao_por_arma: Dict[str, float],
    ) -> Dict[str, Dict[str, float]]:
        """Executa o sistema fuzzy para cada arma e retorna os scores."""
        resultados: Dict[str, Dict[str, float]] = {}

        for weapon in self._weapon_catalog:
            simulador = ctrl.ControlSystemSimulation(weapon["system"])
            simulador.input["distancia"] = distancia_val
            simulador.input["municao"] = municao_por_arma.get(weapon["name"], 0.0)
            simulador.compute()
            score = float(simulador.output.get("desejabilidade", 0.0))

            resultados[weapon["name"]] = {
                "value": score,
                "color": weapon["color"],
            }

        return resultados

    def run(self) -> None:
        print("\n============================================")
        print("  Painel Fuzzy - Escolha de Armas para NPC")
        print("============================================")
        print("Informe valores de 0 a 100. Digite 'sair' para encerrar.\n")

        while True:
            distancia_val = self._prompt_value("Distância do alvo (0-100%): ")
            if distancia_val is None:
                break

            municao_balas: Dict[str, float] = {}
            municao_percentuais: Dict[str, float] = {}

            for weapon in self._weapon_catalog:
                capacidade = weapon.get("ammo_capacity", 0)
                prompt = (
                    f"Munição disponível para {weapon['name']} "
                    f"(0-{capacidade} balas): "
                )
                valor = self._prompt_value(prompt, float(capacidade))
                if valor is None:
                    municao_balas = {}
                    municao_percentuais = {}
                    break

                municao_balas[weapon["name"]] = valor
                if capacidade > 0:
                    percent = (valor / capacidade) * 100.0
                else:
                    percent = 0.0
                municao_percentuais[weapon["name"]] = max(0.0, min(percent, 100.0))

            if len(municao_percentuais) != len(self._weapon_catalog):
                break

            resultados = self.evaluate(distancia_val, municao_percentuais)
            melhor_arma = max(resultados, key=lambda arma: resultados[arma]["value"])

            self._exibir_console(
                distancia_val,
                municao_balas,
                resultados,
                melhor_arma,
            )
            self._exibir_grafico(
                distancia_val,
                municao_percentuais,
                resultados,
                melhor_arma,
            )

            if not self._perguntar_continuacao():
                break

        print("\nSessão encerrada. Obrigado por testar o painel!")

    def _prompt_value(self, prompt: str, max_value: float = 100.0) -> float:
        while True:
            try:
                raw = input(prompt).strip().lower()
                if raw in {"sair", "exit", "q", "quit"}:
                    return None

                value = float(raw.replace(",", "."))
                if 0 <= value <= max_value:
                    return value
                limite_texto = f"{max_value:g}" if max_value >= 1 else f"{max_value:.2f}"
                print(f"Valor fora do intervalo permitido (0-{limite_texto}).")
            except ValueError:
                print("Entrada inválida. Utilize números ou 'sair'.")
            except KeyboardInterrupt:
                print("\nEntrada cancelada pelo usuário.")
                return None

    def _perguntar_continuacao(self) -> bool:
        while True:
            try:
                resposta = input("\nExecutar outro cenário? [s/N]: ").strip().lower()
                if resposta in {"s", "sim"}:
                    print()
                    return True
                if resposta in {"", "n", "nao"}:
                    return False
                print("Entrada inválida. Responda com 's' ou 'n'.")
            except KeyboardInterrupt:
                return False

    def _exibir_console(
        self,
        distancia_val: float,
        municao_balas: Dict[str, float],
        resultados: Dict[str, Dict[str, float]],
        melhor_arma: str,
    ) -> None:
        print("\n+------------------------------------------+")
        print("| Cenário avaliado                         |")
        print("+------------------------------------------+")
        print(f"  Distância do alvo : {distancia_val:5.1f}%")
        print("  Munição disponível por arma:")

        for weapon in self._weapon_catalog:
            nome = weapon["name"]
            capacidade_real = weapon.get("ammo_capacity", 0)
            divisor = capacidade_real if capacidade_real else 1
            balas = municao_balas.get(nome, 0.0)
            percentual = (balas / divisor) * 100.0
            capacidade_texto = capacidade_real if capacidade_real else divisor
            print(
                f"    - {nome:<15}: {balas:5.0f}/{capacidade_texto} balas "
                f"({percentual:5.1f}%)"
            )

        print("\nRanking de desejabilidade")
        print("--------------------------------------------")

        ordenado = sorted(
            resultados.items(), key=lambda item: item[1]["value"], reverse=True
        )

        for posicao, (arma, dados) in enumerate(ordenado, start=1):
            score = dados["value"]
            classificacao = self._classificar(score)
            prefixo = ">>" if arma == melhor_arma else "  "
            print(
                f"{prefixo} {posicao:>2}. {arma:<15} | {score:6.2f}% | {classificacao}"
            )

        print("\nRecomendação")
        print("--------------------------------------------")
        print(f"  Melhor escolha: {melhor_arma}")
        print(f"  Pontuação fuzzy: {resultados[melhor_arma]['value']:.2f}%")

    def _classificar(self, score: float) -> str:
        if score >= 60:
            return "Prioridade máxima"
        if score >= 30:
            return "Recomendado"
        return "Evitar"

    def _exibir_grafico(
        self,
        distancia_val: float,
        municao_percentuais: Dict[str, float],
        resultados: Dict[str, Dict[str, float]],
        melhor_arma: str,
    ) -> None:
        fig = plt.figure(figsize=(15, 5))
        grid = fig.add_gridspec(1, 3)

        ax_dist = fig.add_subplot(grid[0, 0])
        ax_mun = fig.add_subplot(grid[0, 1])
        ax_bar = fig.add_subplot(grid[0, 2])

        self._plot_input(ax_dist, self.distancia, distancia_val, "Distância")
        municao_para_plot = municao_percentuais.get(melhor_arma, 0.0)
        titulo_municao = f"Munição ({melhor_arma})"
        self._plot_input(ax_mun, self.municao, municao_para_plot, titulo_municao)
        self._plot_bar(ax_bar, resultados, melhor_arma)

        fig.suptitle(
            "Sistema Fuzzy NPC - Seleção de Armas\n"
            f"Distância: {distancia_val:.1f}% | Munição {melhor_arma}: {municao_para_plot:.1f}%",
            fontsize=15,
            fontweight="bold",
        )
        fig.tight_layout(rect=(0, 0, 1, 0.9))

        try:
            plt.show()
        except Exception:
            fig.savefig("npc_fuzzy_last_result.png", dpi=160)
            print("⚠️ Ambiente sem suporte gráfico. Resultado salvo em npc_fuzzy_last_result.png")
        finally:
            plt.close(fig)

    def _plot_input(self, ax, variable: ctrl.Antecedent, val: float, title: str) -> None:
        xmin = float(variable.universe.min())
        xmax = float(variable.universe.max())
        span = xmax - xmin
        margin = max(span * 0.04, 2.0)

        lines = []
        for label in variable.terms:
            mf = variable[label].mf
            line, = ax.plot(variable.universe, mf, label=label)
            ax.fill_between(
                variable.universe,
                0,
                mf,
                color=line.get_color(),
                alpha=0.08,
            )
            lines.append((label, line, mf))

            max_val = mf.max()
            peak_indices = np.flatnonzero(np.isclose(mf, max_val))
            peak_x = variable.universe[peak_indices].mean() if peak_indices.size else val
            label_y = min(max_val + 0.08, 1.1)
            label_x = float(peak_x)
            halign = "center"

            if label_x <= xmin + margin:
                label_x = xmin + margin
                halign = "left"
            elif label_x >= xmax - margin:
                label_x = xmax - margin
                halign = "right"

            ax.text(
                label_x,
                label_y,
                label.capitalize(),
                color=line.get_color(),
                ha=halign,
                va="bottom",
                fontsize=9,
                fontweight="bold",
                clip_on=False,
            )

        ax.axvline(val, color="gray", linestyle="--", linewidth=1)

        memberships = {}
        for label, line, mf in lines:
            membership = fuzz.interp_membership(
                variable.universe, mf, val
            )
            memberships[label] = membership
            if membership > 0:
                ax.scatter(
                    [val],
                    [membership],
                    color=line.get_color(),
                    edgecolor="black",
                    zorder=5,
                    s=35,
                )

        ax.set_title(f"{title} (valor = {val:.1f})")
        ax.set_xlabel(title)
        ax.set_ylabel("Grau de pertinência")
        ax.set_xlim(variable.universe.min(), variable.universe.max())
        ax.set_ylim(-0.05, 1.15)

    def _plot_bar(
        self,
        ax,
        resultados: Dict[str, Dict[str, float]],
        melhor_arma: str,
    ) -> None:
        armas = list(resultados.keys())
        valores = [resultados[arma]["value"] for arma in armas]
        cores = [resultados[arma]["color"] for arma in armas]

        barras = ax.bar(armas, valores, color=cores, alpha=0.85, edgecolor="black", linewidth=2)

        if melhor_arma in armas:
            idx = armas.index(melhor_arma)
            barras[idx].set_linewidth(4)
            barras[idx].set_alpha(1.0)

        for barra, valor in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                valor + 2,
                f"{valor:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        ax.axhline(30, color="orange", linestyle="--", alpha=0.7, label="Limiar Desejável")
        ax.axhline(60, color="green", linestyle="--", alpha=0.7, label="Limiar Essencial")

        ax.set_ylabel("Desejabilidade (%)")
        ax.set_xlabel("Armas")
        ax.set_ylim(0, 110)
        ax.set_title("Comparação das armas")
        ax.grid(axis="y", alpha=0.3)
        ax.legend()

def main() -> None:
    app = NPCFuzzyWeaponSelector()
    app.run()


if __name__ == "__main__":
    main()
