from selenium import webdriver
from selenium.webdriver.common.by import By

import requests
import os
import time
import threading


BASE_URL = "https://ccis.ccit-ftui.com"
loading_active = False
download_count = 0


def clear_terminal():

    os.system(
        "cls" if os.name == "nt"
        else "clear"
    )


def animate_download():

    global loading_active
    global download_count

    dots = 0

    while loading_active:

        print(
            f"\rDownloading files ({download_count})"
            + "." * dots
            + "   ",
            end="",
            flush=True
        )

        dots = (dots + 1) % 4

        time.sleep(0.3)


def create_driver():

    print("\nChoose yo browser:")
    print("1. Chrome")
    print("2. Edge")
    print("3. Firefox")

    choice = input("\nChoose: ")

    if choice == "1":
        return webdriver.Chrome()

    elif choice == "2":
        return webdriver.Edge()

    return webdriver.Firefox()


def create_session(driver):

    session = requests.Session()

    for cookie in driver.get_cookies():

        session.cookies.set(
            cookie["name"],
            cookie["value"]
        )

    return session


def get_class_links(driver):

    driver.get(
        f"{BASE_URL}/student-home/my-class"
    )

    time.sleep(3)

    class_links = []

    for link in driver.find_elements(
        By.TAG_NAME,
        "a"
    ):

        href = link.get_attribute("href")

        if not href:
            continue

        if (
            "/student-home/my-class/" in href
            and "/show" in href
        ):

            if href not in class_links:

                class_links.append(href)

    return class_links


def get_project_links(driver, class_url):

    driver.get(class_url)

    time.sleep(2)

    project_links = []

    for link in driver.find_elements(
        By.TAG_NAME,
        "a"
    ):

        href = link.get_attribute("href")

        if not href:
            continue

        if (
            "/module-project/" in href
            and "/edit" in href
        ):

            if href not in project_links:

                project_links.append(href)

    return project_links


def download_file(
    session,
    file_url,
    filename,
    download_folder
):

    os.makedirs(
        download_folder,
        exist_ok=True
    )

    filepath = os.path.join(
        download_folder,
        filename
    )

    if os.path.exists(filepath):

        return

    response = session.get(
        file_url,
        timeout=30
    )

    if response.status_code == 200:

        with open(
            filepath,
            "wb"
        ) as f:

            f.write(response.content)


def download_project_files(
    driver,
    session,
    project_url
):

    driver.get(project_url)

    time.sleep(2)

    links = driver.find_elements(
        By.CSS_SELECTOR,
        "a[download]"
    )

    return links


def print_banner():

    print(r"""
 ██████╗ ██████╗ ██╗███████╗      ███╗   ██╗ ██████╗
██╔════╝██╔════╝ ██║██╔════╝      ████╗  ██║██╔════╝
██║     ██║      ██║███████╗█████╗██╔██╗ ██║██║  ███╗
██║     ██║      ██║╚════██║╚════╝██║╚██╗██║██║   ██║
╚██████╗╚██████╗ ██║███████║      ██║ ╚████║╚██████╔╝
 ╚═════╝ ╚═════╝ ╚═╝╚══════╝      ╚═╝  ╚═══╝ ╚═════╝

            AUTOMATED FILES DOWNLOADER
              for CCIT-FTUI Students
""")


def main():

    print_banner()

    download_folder = input(
        "\nEnter the new folder name: "
    ).strip()

    if not download_folder:
        download_folder = "Project_Files_Backup"

    driver = create_driver()

    driver.get(BASE_URL)

    while True:

        print("\rWaiting yo slow ass finger to input the credential..",
              end="", flush=True)

        if "dashboard" in driver.current_url:
            break

        time.sleep(0.2)

    print("\n Login Detected")
    time.sleep(1)

    clear_terminal()
    print_banner()

    session = create_session(driver)

    driver.minimize_window()

    class_links = get_class_links(driver)

    print("\nScanning classes..")
    print(f"Found {len(class_links)} classes")

    time.sleep(1)

    clear_terminal()
    print_banner()
    downloaded = set()

    global loading_active
    global download_count

    download_count = 0
    loading_active = True

    animation_thread = threading.Thread(
        target=animate_download
    )

    animation_thread.start()

    for class_url in class_links:

        project_links = get_project_links(
            driver,
            class_url
        )

        for project_url in project_links:

            file_links = download_project_files(
                driver,
                session,
                project_url
            )

            for link in file_links:

                file_url = link.get_attribute(
                    "href"
                )

                filename = link.get_attribute(
                    "download"
                )

                if not file_url:
                    continue

                if file_url in downloaded:
                    continue

                downloaded.add(file_url)

                download_count += 1

                download_file(
                    session,
                    file_url,
                    filename,
                    download_folder
                )

    loading_active = False

    animation_thread.join()

    print("\r" + " " * 80, end="")
    print("\r", end="")
    print("_" * 40)
    print("Files saved at ", os.path.abspath(download_folder))
    print(
        f"\nFiles downloaded {download_count}, so this sht is done.. gudluckk!")

    driver.quit()


if __name__ == "__main__":
    main()
