import requests
from datetime import datetime, timedelta

cloudflare_api_key = 'xxxxx'
telegram_bot_token = 'xxxxx'
telegram_chat_id = '12345'

zone_list_url = 'https://api.cloudflare.com/client/v4/zones'

headers = {
    'Authorization': f'Bearer {cloudflare_api_key}',
    'Content-Type': 'application/json'
}

response = requests.get(zone_list_url, headers=headers)

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(telegram_url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send Telegram message. Status code: {response.status_code}, Response: {response.text}")

if response.status_code == 200:
    zones_data = response.json()['result']

    today_utc_minus_7 = datetime.utcnow() - timedelta(hours=7)

    for zone_info in zones_data:
        zone_id = zone_info['id']
        zone_name = zone_info['name']

        page = 1
        while True:
            dns_record_url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?page={page}'

            response = requests.get(dns_record_url, headers=headers)

            if response.status_code == 200:
                dns_records = response.json()['result']

                for record in dns_records:
                    created_on_date = datetime.strptime(record['created_on'], "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(hours=7)
                    modified_on_date = datetime.strptime(record['modified_on'], "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(hours=7)
                    if created_on_date.date() == today_utc_minus_7.date() or modified_on_date.date() == today_utc_minus_7.date():
                        message = "<b>New or modified DNS record detected:</b>\n"
                        message += f"Type: {record['type']}\n"
                        message += f"Name: {record['name']}\n"
                        message += f"Content: {record['content']}\n"
                        message += f"Created On: {record['created_on']}\n"
                        message += f"Modified On: {record['modified_on']}\n"
                        print(message)
                        send_telegram_message(message)
                result_info = response.json()['result_info']
                total_pages = result_info['total_pages']
                if page >= total_pages:
                    break
                else:
                    page += 1
            else:
                print(f"Error fetching DNS records for Zone ID {zone_id}: {response.status_code}, Message: {response.text}")
else:
    print(f"Error: {response.status_code}, Message: {response.text}")
