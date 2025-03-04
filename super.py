import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Настройка браузера
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Функция для сохранения данных в CSV
def save_to_csv(data, filename="results.csv"):
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Название", "Компания", "Локация", "Ссылка", "Опыт", "Ключевые навыки", "Описание", "Мин. зарплата (₽)", "Макс. зарплата (₽)"])
        writer.writerows(data)
    print(f"Данные сохранены в файл {filename}")

# Список IT-специальностей для поиска
it_specialties = [
    "Программист", "Разработчик"]

try:
    # Открываем сайт SuperJob
    print("Открываю сайт...")
    driver.get("https://www.superjob.ru")

    # Ждем загрузки страницы
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("HTML страницы загружен!")

    all_results = []

    for specialty in it_specialties:
        print(f"Ищу вакансии по специальности: {specialty}")

        # Ищем поле поиска
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='keywords']"))
        )
        search_box.clear()
        search_box.send_keys(specialty)

        # Нажимаем кнопку поиска
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        search_button.click()
        print("Кнопка 'Найти' нажата!")

        # Ждем загрузки результатов
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'f-test-search-result')]"))
        )
        print("Результаты поиска загружены!")

        # Сбор данных
        vacancies = driver.find_elements(By.XPATH, "//div[contains(@class, 'f-test-vacancy-item')]")

        for vacancy in vacancies:
            try:
                title_element = vacancy.find_element(By.XPATH, ".//a[contains(@class, 'f-test-link')]")
                title = title_element.text.strip()
                link = title_element.get_attribute("href")

                try:
                    company = vacancy.find_element(By.XPATH, ".//span[contains(@class, 'f-test-text-vacancy-item-company-name')]").text.strip()
                except:
                    company = "Не указана"

                try:
                    location = vacancy.find_element(By.XPATH, ".//span[contains(@class, 'f-test-text-company-item-location')]").text.strip()
                except:
                    location = "Не указано"

                try:
                    salary_text = vacancy.find_element(By.XPATH, ".//span[contains(@class, 'f-test-text-company-item-salary')]").text.strip()
                    min_salary, max_salary = None, None
                    if "—" in salary_text:
                        min_salary, max_salary = map(lambda x: x.replace("₽", "").replace(" ", ""), salary_text.split("—"))
                    elif "от" in salary_text:
                        min_salary = salary_text.replace("от", "").replace("₽", "").replace(" ", "").strip()
                    elif "до" in salary_text:
                        max_salary = salary_text.replace("до", "").replace("₽", "").replace(" ", "").strip()
                    else:
                        min_salary, max_salary = salary_text.replace("₽", "").replace(" ", ""), None
                except:
                    min_salary, max_salary = "Не указана", "Не указана"

                # Переход на страницу вакансии
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)

                try:
                    experience = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Опыт работы')]/following-sibling::span"))
                    ).text.strip()
                except:
                    experience = "Не указан"

                try:
                    description = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'f-test-vacancy-description')]"))
                    ).text.strip()
                except:
                    description = "Не указано"

                try:
                    skills = driver.find_element(By.XPATH, "//div[contains(@class, 'f-test-tags')]").text.strip()
                except:
                    skills = "Не указаны"

                # Добавляем данные
                all_results.append([title, company, location, link, experience, skills, description, min_salary, max_salary])

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"Ошибка при обработке вакансии: {e}")

        print(f"Собрано {len(all_results)} вакансий для '{specialty}'!")
        time.sleep(3)

    # Сохраняем данные
    save_to_csv(all_results)

except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    driver.quit()
