from typing import Any, Dict, List

ACCOUNTS: List[Dict[str, Any]] = [
    # {
    #     "name": "Sushi Story",
    #     "fb_account_id": "act_2104155906861221",
    #     "spreadsheet_id": "1NUdszjTceq_7dmyGlg9blkjGh_CRySbHtR0NdjmBj2U",
    #     # необязательно: свой column_map / header_row, если отличается от дефолтного
    # },
    # {
    #     "name": "Zavadskaya Психолог",
    #     "fb_account_id": "act_1049164820952752",
    #     "spreadsheet_id": "1hsreO0swPQvIccVSD3Brx5Klt63V-MwFvsZljCRtBHI",
    # },
    {
        "name": "Flesh Sushi",
        "fb_account_id": "act_768353842892618",
        "spreadsheet_id": "13FeSY3r6Mw_SIg1YDCNHBodeJx9n9OUe4gjjhy1U0g8",
        # У этого кабинета вместо обычной классификации purchase/message —
        # своя кастомная конверсия "order_status" (ID 2053331442068952).
        # "custom_requests_action_type" НЕ проверен на реальных данных —
        # прогоните inspect_actions.py на этом кабинете и сверьте с тем,
        # что видите в Ads Manager по этой кастомной конверсии; если имя
        # окажется другим — поправьте строку ниже.
        "custom_requests_action_type": "offsite_conversion.custom.2053331442068952",
    },
    # {
    #     "name": "Valeri Flowers",
    #     "fb_account_id": "act_1498849214543354",
    #     "spreadsheet_id": "1Dv03NLxKFzTDqNyctZxxc6y0xYIJ0_qcbnT_Ru4qJp4",
    # },
    # {
    #     # Пример: ОДИН рекламный аккаунт, который ведёт рекламу на НЕСКОЛЬКО
    #     # услуг сразу (например, эпиляция и барбер) — данные нужно развести
    #     # по разным таблицам. Вместо "spreadsheet_id" на верхнем уровне здесь
    #     # список "services": каждая услуга ищет СВОИ ключевые слова в названии
    #     # кампании (без учёта регистра, срабатывает по любому вхождению) и
    #     # пишет только в свою таблицу. Meta запрашивается один раз в день на
    #     # этот аккаунт, а не по разу на каждую услугу.
    #     #
    #     # Кампания, в названии которой не найдётся НИ ОДНОГО из ключевых слов
    #     # ни одной услуги, просто не попадёт ни в одну таблицу — это не
    #     # логируется отдельно (в отличие от "не удалось определить тип
    #     # заявки"), так что периодически стоит проверять в Ads Manager,
    #     # что все ваши кампании действительно называются с учётом этих слов.
    #     "name": "Hells",
    #     "fb_account_id": "act_280381074046319",
    #     "services": [
    #         {
    #             "name": "Epil",
    #             "keywords": ["epil", "laser", "epilacia laserowa", "dl", "l", "depilacia", "depil", "depilacia laserowa"],
    #             "spreadsheet_id": "1YvKOsOxIaluGHfSaHRnINtpGqMAKs0dslObr-CS83ek",
    #             # можно также указать свои column_map / header_row /
    #             # custom_requests_action_type — если не указать, возьмутся
    #             # значения по умолчанию (DEFAULT_COLUMN_MAP и т.д.)
    #         },
    #         {
    #             "name": "Barber",
    #             "keywords": ["barber", "барбер"],
    #             "spreadsheet_id": "1k8gPUTsDUzEwD4qA9EQZW1bVJ-pe2QqJeY945ucRMwI",
    #         },
    #         {
    #             "name": "other",
    #             "is_catch_all": True,
    #             "spreadsheet_id": "1HD_lISflmio3HKyz7LhTdVeVxM0PBQKKha-gqbVV4bk",
    #         },
    #     ],
    # },
    # {
    #     "name": "Bur Bur",
    #     "fb_account_id": "act_4258098044453528",
    #     "spreadsheet_id": "1JBq3IG2bBnzAg7Z6AbYxpLpXOL7gM1_gkHVI18uY8Ms",
    #     "custom_requests_action_type": "offsite_conversion.custom.1536830724578373",
    # },
    # {
    #     "name": "CD",
    #     "fb_account_id": "act_1284950825579466",
    #     "spreadsheet_id": "1d7wcpp2qeZCCaqkOrQFh95qLPa273JmJRaVm-Hs5h14",
    # },
    # {
    #     "name": "Массаж",
    #     "fb_account_id": "act_678481241285112",
    #     "spreadsheet_id": "1lxU-_Do-Hpily58-aWiDEF94tDAsi6dJWkKdaG0UClk",
    # },
    # # ... добавьте остальные кабинеты по аналогии
]