import PyMCTranslate


def main():
    translations = PyMCTranslate.new_translation_manager()

    print(1, translations.get_version("java", (1, 13, 2)).version_number)
    print(2, translations.get_version("java", [1, 13, 2]).version_number)
    print(3, translations.get_version("java", 1200).version_number)  # 1.12.2
    print(4, translations.get_version("java", 1531).version_number)  # 1.13.2
    print(5, translations.get_version("java", 1631).version_number)
    print(6, translations.get_version("java", 1731).version_number)


if __name__ == "__main__":
    main()
