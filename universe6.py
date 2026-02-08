import random


class LongTermStressModel:
    def __init__(self):
        # Вводные данные из прогноза 2026-2031
        self.years = [2026, 2027, 2028, 2029, 2030, 2031]
        self.base_strain = 0.88  # System Strain
        self.ai_incident_prob = 0.65  # Риск инцидента в 2027
        self.normalization = 0.90  # Привыкание масс к хаосу

    def run_projection(self):
        current_strain = self.base_strain
        results = {}

        for year in self.years:
            # Эффект накопленной усталости (Entropy)
            entropy = (year - 2025) * 0.05

            # Фактор Прокси-эскалации (размазывание конфликта)
            proxy_factor = random.uniform(0.1, 0.3)

            # Расчет риска коллапса (не только войны, но и падения систем)
            risk_score = current_strain + entropy + proxy_factor

            # Учет "Черного Лебедя" ИИ в 2027
            if year == 2027:
                risk_score += self.ai_incident_prob * 0.5

            # Коэффициент сдерживания (падает с каждым годом)
            deterrence = 1.1 - (entropy * 0.8)

            # Вероятность того, что "управляемое" станет "неуправляемым"
            break_point = risk_score > deterrence
            results[year] = {"risk": round(risk_score, 2), "collapsed": break_point}

            # Наращиваем нагрузку для следующего года
            current_strain += 0.02

        return results


# --- ЗАПУСК ---
model = LongTermStressModel()
projection = model.run_projection()

print("--- АНАЛИЗ ПЕРИОДА 2026-2031 (VANGUARD) ---")
for year, data in projection.items():
    status = "🔥 COLLAPSE" if data['collapsed'] else "🧊 MANAGED STRESS"
    print(f"Год {year}: Индекс нагрузки {data['risk']} | Статус: {status}")