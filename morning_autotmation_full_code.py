# Standard library imports
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

# Third-party library imports
import requests  # pip install requests
from dotenv import load_dotenv  # pip install python-dotenv
from todoist_api_python.api import TodoistAPI  # pip install todoist-api-python


# Load environment variables from .env file
def load_environment_variables():
    """Load environment variables from the .env file."""
    try:
        # Try to get the directory where the script is located.
        # This will work when the script is run as a file.
        script_dir = Path(__file__).resolve().parent
    except NameError:
        # If __file__ is not defined (like in a Jupyter notebook), get the cwd instead.
        script_dir = Path(os.getcwd())
    env_file_path = script_dir / ".env"
    load_dotenv(env_file_path)
    
    
def get_news(news_api_key):
    """Fetch the latest news articles containing the keyword 'chatgpt'."""
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        params = {
            "access_key": news_api_key,
            "keywords": "chatgpt",
            "languages": "en",
            "sort": "published_desc",
            "date": current_date,
            "limit": 3,
        }

        response = requests.get("http://api.mediastack.com/v1/news", params=params)
        response.raise_for_status()
        news_items = response.json()["data"]

        news_text = "\n\n".join(
            f"Title: {item.get('title', 'No title provided')}\n"
            f"Description: {item.get('description', 'No description provided')}\n"
            f"URL: {item.get('url', 'No URL provided')}"
            for item in news_items
        )

        return news_text
    except requests.RequestException as e:
        return f"News information is currently unavailable. Error: {e}"


def get_weather(api_key, city_name, country_code):
    """Fetch the current weather for a given city and country."""
    try:
        api_url = f"https://api.weatherbit.io/v2.0/current?city={city_name}&country={country_code}&key={api_key}"
        response = requests.get(api_url)
        response.raise_for_status()

        weather_data = response.json()["data"][0]
        weather_report = (
            f"Currently, the weather in {weather_data['city_name']}, {weather_data['country_code']} "
            f"is {weather_data['temp']}°C with {weather_data['weather']['description']}."
        )
        return weather_report
    except requests.RequestException:
        return "Weather information is currently unavailable."


def get_tasks(todoist_api_key):
    """Retrieve open tasks from Todoist."""
    try:
        api = TodoistAPI(todoist_api_key)
        tasks = api.get_tasks()
        tasks_content = [task.content for task in tasks]
        return f"Here are your open tasks: {', '.join(tasks_content)}"
    except Exception:
        return "Could not retrieve tasks."


def send_email(
    sender, recipient, subject, message_body, smtp_server, smtp_port, password
):
    """Send an email using the specified SMTP server and login credentials."""
    try:
        email = EmailMessage()
        email["From"] = sender
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(message_body)

        with smtplib.SMTP(smtp_server, port=smtp_port) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(email)
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email. Error: {e}"


def main():
    load_environment_variables()

    # Retrieve sensitive data
    news_api_key = os.getenv("NEWS_API_KEY")
    todoist_api_key = os.getenv("TODOIST_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    # Email config
    SMTP_SERVER = "smtp-mail.outlook.com"
    SMTP_PORT = 587

    news = get_news(news_api_key)
    weather = get_weather(weather_api_key, "Dresden", "DE")
    tasks = get_tasks(todoist_api_key)

    # Create the email body with separated sections
    message_body = (
        "Good morning! Here's your update:\n\n"
        "---- NEWS ----\n\n"
        f"{news}\n\n"
        "---- WEATHER ----\n\n"
        f"{weather}\n\n"
        "---- TO-DO LIST ----\n\n"
        f"{tasks}\n"
    )

    # Send the email to the sender
    email_status = send_email(
        sender=sender,
        recipient=sender,  # sending email to myself
        subject="Your Morning Update 🚀",
        message_body=message_body,
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        password=password,
    )
    print(email_status)


if __name__ == "__main__":
    main()