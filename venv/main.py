import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Загрузка ключей
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
APOLLO_KEY = os.getenv("APOLLO_API_KEY")


def find_target_leads():
    url = "https://api.apollo.io"
    headers = {
        "X-Api-Key": APOLLO_KEY,
        "Content-Type": "application/json"
    }
    # Ищем Digital-директоров в Azercell и других телекомах Баку
    data = {
        "q_organization_domains": "azercell.com\nbakcell.com\narazmarket.az",
        "person_titles": ["Head of Digital", "CTO", "Marketing Director"],
        "display_mode": "explorer"
    }

    res = requests.post(url, headers=headers, json=data)
    return res.json().get('people', [])


def generate_pitch(name, company, title):
    prompt = f"Write a professional cold email to {name}, {title} at {company}. " \
             f"Mention the pain: lack of digital tools for regions in Azerbaijan. " \
             f"Offer a 10-min call. Short and punchy."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # 3.5 дешевле и быстрее для тестов
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices.message.content


# --- СТАРТ ---
print("🚀 Агент запущен. Ищу контакты в Баку...")
leads = find_target_leads()

if leads:
    first_lead = leads[0]
    name = first_lead.get('first_name', 'Professional')
    comp = first_lead.get('organization', {}).get('name', 'your company')

    print(f"✅ Нашел лида: {name} из {comp}")

    pitch = generate_pitch(name, comp, first_lead.get('title'))
    print("-" * 30)
    print(f"📧 СГЕНЕРИРОВАННОЕ ПИСЬМО:\n\n{pitch}")
    print("-" * 30)
else:
    print("❌ Лиды не найдены. Проверь баланс в Apollo или фильтры.")
