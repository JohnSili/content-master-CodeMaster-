from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Создаем экземпляр браузера
driver = webdriver.Chrome()

# Открываем страницу
driver.get("https://lordfilm.ai/1407-ne-bespokojsja-dorogaja-2022.html")

# Ждем, пока страница загрузится
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fa-thumbs-down")))

# Находим элемент "Не нравится"
dislike_button = driver.find_element(By.CSS_SELECTOR, ".fa-thumbs-down")

# Нажимаем на элемент
dislike_button.click()

# Закрываем браузер
driver.quit()