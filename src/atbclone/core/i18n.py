"""Internationalization (i18n) module for ATBClone.

Automatically detects current macOS system language or environment preferences
and provides translated UI strings for CLI commands, interactive wizards, and messages.
Supports English (en), Simplified Chinese (zh), Traditional Chinese (zh_TW),
Japanese (ja), Korean (ko), German (de), French (fr), Russian (ru), and Spanish (es).
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Any

SUPPORTED_LANGUAGES = ("en", "zh", "zh_TW", "ja", "ko", "de", "fr", "ru", "es")
_current_lang: str | None = None

MESSAGES: dict[str, dict[str, str]] = {
    # --- Wizard Command ---
    "wizard_title": {
        "en": "🧙 ATBClone Wizard\n",
        "zh": "🧙 ATBClone 小向导\n",
        "zh_TW": "🧙 ATBClone 小精靈\n",
        "ja": "🧙 ATBClone ウィザード\n",
        "ko": "🧙 ATBClone 마법사\n",
        "de": "🧙 ATBClone Assistent\n",
        "fr": "🧙 Assistant ATBClone\n",
        "ru": "🧙 Мастер ATBClone\n",
        "es": "🧙 Asistente ATBClone\n",
    },
    "wizard_prompt_app_path": {
        "en": "Please enter the .app path to clone",
        "zh": "请输入要分身的 .app 路径",
        "zh_TW": "請輸入要分身的 .app 路徑",
        "ja": "クローン対象の .app パスを入力してください",
        "ko": "복제할 .app 경로를 입력하세요",
        "de": "Bitte geben Sie den .app-Pfad zum Klonen ein",
        "fr": "Veuillez entrer le chemin du fichier .app à cloner",
        "ru": "Пожалуйста, введите путь к приложению .app для клонирования",
        "es": "Por favor, introduzca la ruta del archivo .app a clonar",
    },
    "wizard_err_invalid_app_path": {
        "en": "[bold red]Error: Path does not exist or is not a .app application, please try again.[/bold red]",
        "zh": "[bold red]错误: 路径不存在或不是 .app 应用，请重新输入。[/bold red]",
        "zh_TW": "[bold red]錯誤: 路徑不存在或不是 .app 應用程式，請重新輸入。[/bold red]",
        "ja": "[bold red]エラー: パスが存在しないか、.app アプリケーションではありません。再入力してください。[/bold red]",
        "ko": "[bold red]오류: 경로가 존재하지 않거나 .app 애플리케이션이 아닙니다. 다시 입력해 주세요.[/bold red]",
        "de": "[bold red]Fehler: Pfad existiert nicht oder ist keine .app-Anwendung. Bitte erneut versuchen.[/bold red]",
        "fr": "[bold red]Erreur : Le chemin n'existe pas ou n'est pas une application .app, veuillez réessayer.[/bold red]",
        "ru": "[bold red]Ошибка: Путь не существует или не является приложением .app, попробуйте снова.[/bold red]",
        "es": "[bold red]Error: La ruta no existe o no es una aplicación .app, inténtelo de nuevo.[/bold red]",
    },
    "wizard_detecting_app": {
        "en": "\nDetecting application...",
        "zh": "\n检测应用...",
        "zh_TW": "\n正在偵測應用程式...",
        "ja": "\nアプリケーションを検出中...",
        "ko": "\n애플리케이션 감지 중...",
        "de": "\nAnwendung wird analysiert...",
        "fr": "\nDétection de l'application...",
        "ru": "\nОпределение приложения...",
        "es": "\nDetectando aplicación...",
    },
    "wizard_app_info": {
        "en": "Application: {app_name} ({bundle_id})",
        "zh": "应用: {app_name} ({bundle_id})",
        "zh_TW": "應用程式: {app_name} ({bundle_id})",
        "ja": "アプリ: {app_name} ({bundle_id})",
        "ko": "앱: {app_name} ({bundle_id})",
        "de": "Anwendung: {app_name} ({bundle_id})",
        "fr": "Application : {app_name} ({bundle_id})",
        "ru": "Приложение: {app_name} ({bundle_id})",
        "es": "Aplicación: {app_name} ({bundle_id})",
    },
    "wizard_strategy_info": {
        "en": "Strategy: {strategy}\n",
        "zh": "策略: {strategy}\n",
        "zh_TW": "策略: {strategy}\n",
        "ja": "戦略: {strategy}\n",
        "ko": "전략: {strategy}\n",
        "de": "Strategie: {strategy}\n",
        "fr": "Stratégie : {strategy}\n",
        "ru": "Стратегия: {strategy}\n",
        "es": "Estrategia: {strategy}\n",
    },
    "wizard_prompt_clone_name": {
        "en": "Clone name",
        "zh": "分身名称",
        "zh_TW": "分身名稱",
        "ja": "クローン名",
        "ko": "클론 이름",
        "de": "Klon-Name",
        "fr": "Nom du clone",
        "ru": "Имя клона",
        "es": "Nombre del clon",
    },
    "wizard_prompt_display_name": {
        "en": "Dock/Finder display name (supports Unicode, leave empty to match clone name)",
        "zh": "Dock/Finder 显示名称（支持中文，留空与分身名称相同）",
        "zh_TW": "Dock/Finder 顯示名稱（支援自訂字元，留空則與分身名稱相同）",
        "ja": "Dock/Finder 表示名（空白の場合はクローン名と同じ）",
        "ko": "Dock/Finder 표시 이름 (비워두면 클론 이름과 동일)",
        "de": "Dock/Finder-Anzeigename (leer lassen für Klon-Namen)",
        "fr": "Nom d'affichage Dock/Finder (laisser vide pour utiliser le nom du clone)",
        "ru": "Отображаемое имя в Dock/Finder (оставьте пустым для имени клона)",
        "es": "Nombre para mostrar en Dock/Finder (dejar en blanco para usar el nombre del clon)",
    },
    "wizard_prompt_icon": {
        "en": "Custom icon path (.icns, leave empty for original app icon)",
        "zh": "自定义图标路径（.icns，留空使用原始 app 图标）",
        "zh_TW": "自訂圖示路徑（.icns，留空則使用原始 app 圖示）",
        "ja": "カスタムアイコンのパス（.icns、空白の場合は元のアイコン）",
        "ko": "사용자 지정 아이콘 경로 (.icns, 비워두면 원본 아이콘)",
        "de": "Benutzerdefinierter Symbolpfad (.icns, leer lassen für Originalsymbol)",
        "fr": "Chemin de l'icône personnalisée (.icns, laisser vide pour l'icône d'origine)",
        "ru": "Путь к значку (.icns, оставьте пустым для исходного значка)",
        "es": "Ruta de icono personalizado (.icns, dejar en blanco para el icono original)",
    },
    "wizard_err_icon_not_found": {
        "en": "[bold red]Error: File does not exist, please try again.[/bold red]",
        "zh": "[bold red]错误: 文件不存在，请重新输入。[/bold red]",
        "zh_TW": "[bold red]錯誤: 檔案不存在，請重新輸入。[/bold red]",
        "ja": "[bold red]エラー: ファイルが存在しません。再入力してください。[/bold red]",
        "ko": "[bold red]오류: 파일이 존재하지 않습니다. 다시 입력해 주세요.[/bold red]",
        "de": "[bold red]Fehler: Datei existiert nicht, bitte erneut versuchen.[/bold red]",
        "fr": "[bold red]Erreur : Le fichier n'existe pas, veuillez réessayer.[/bold red]",
        "ru": "[bold red]Ошибка: Файл не существует, попробуйте снова.[/bold red]",
        "es": "[bold red]Error: El archivo no existe, inténtelo de nuevo.[/bold red]",
    },
    "wizard_err_icon_not_icns": {
        "en": "[bold red]Error: Must be a .icns file, please try again.[/bold red]",
        "zh": "[bold red]错误: 必须是 .icns 文件，请重新输入。[/bold red]",
        "zh_TW": "[bold red]錯誤: 必須是 .icns 檔案，請重新輸入。[/bold red]",
        "ja": "[bold red]エラー: .icns ファイルである必要があります。再入力してください。[/bold red]",
        "ko": "[bold red]오류: .icns 파일이어야 합니다. 다시 입력해 주세요.[/bold red]",
        "de": "[bold red]Fehler: Muss eine .icns-Datei sein, bitte erneut versuchen.[/bold red]",
        "fr": "[bold red]Erreur : Doit être un fichier .icns, veuillez réessayer.[/bold red]",
        "ru": "[bold red]Ошибка: Файл должен иметь расширение .icns, попробуйте снова.[/bold red]",
        "es": "[bold red]Error: Debe ser un archivo .icns, inténtelo de nuevo.[/bold red]",
    },
    "wizard_prompt_output_dir": {
        "en": "Output directory",
        "zh": "输出目录",
        "zh_TW": "輸出目錄",
        "ja": "出力先ディレクトリ",
        "ko": "출력 디렉토리",
        "de": "Ausgabeverzeichnis",
        "fr": "Répertoire de destination",
        "ru": "Папка назначения",
        "es": "Directorio de destino",
    },
    "wizard_prompt_data_dir": {
        "en": "Data storage directory",
        "zh": "数据存储目录",
        "zh_TW": "資料儲存目錄",
        "ja": "データ保存ディレクトリ",
        "ko": "데이터 저장 디렉토리",
        "de": "Datenspeicherverzeichnis",
        "fr": "Dossier de stockage des données",
        "ru": "Каталог хранения данных",
        "es": "Directorio de almacenamiento de datos",
    },

    "wizard_prompt_use_proxy": {
        "en": "Configure proxy",
        "zh": "是否配置代理",
        "zh_TW": "是否設定代理伺服器",
        "ja": "プロキシを設定しますか",
        "ko": "프록시를 설정하시겠습니까",
        "de": "Proxy konfigurieren",
        "fr": "Configurer un proxy",
        "ru": "Настроить прокси",
        "es": "Configurar proxy",
    },
    "wizard_prompt_proxy_host": {
        "en": "Proxy host",
        "zh": "代理地址",
        "zh_TW": "代理伺服器位址",
        "ja": "プロキシホスト",
        "ko": "프록시 호스트",
        "de": "Proxy-Host",
        "fr": "Hôte du proxy",
        "ru": "Хост прокси",
        "es": "Host del proxy",
    },
    "wizard_prompt_proxy_port": {
        "en": "Proxy port",
        "zh": "代理端口",
        "zh_TW": "代理伺服器連接埠",
        "ja": "プロキシポート",
        "ko": "프록시 포트",
        "de": "Proxy-Port",
        "fr": "Port du proxy",
        "ru": "Порт прокси",
        "es": "Puerto del proxy",
    },
    "wizard_prompt_proxy_type": {
        "en": "Proxy type",
        "zh": "代理类型",
        "zh_TW": "代理伺服器類型",
        "ja": "プロキシタイプ",
        "ko": "프록시 유형",
        "de": "Proxy-Typ",
        "fr": "Type de proxy",
        "ru": "Тип прокси",
        "es": "Tipo de proxy",
    },
    "wizard_confirm_title": {
        "en": "\nAbout to create clone:",
        "zh": "\n即将创建分身:",
        "zh_TW": "\n即將建立分身:",
        "ja": "\nクローンを作成します:",
        "ko": "\n클론을 생성합니다:",
        "de": "\nKlon wird erstellt:",
        "fr": "\nCréation du clone imminente :",
        "ru": "\nСоздание клона:",
        "es": "\nA punto de crear el clon:",
    },
    "wizard_confirm_name": {
        "en": "  Name: {clone_name}",
        "zh": "  名称: {clone_name}",
        "zh_TW": "  名稱: {clone_name}",
        "ja": "  名前: {clone_name}",
        "ko": "  이름: {clone_name}",
        "de": "  Name: {clone_name}",
        "fr": "  Nom : {clone_name}",
        "ru": "  Имя: {clone_name}",
        "es": "  Nombre: {clone_name}",
    },
    "wizard_confirm_display_name": {
        "en": "  Display Name: {display_name}",
        "zh": "  显示名称: {display_name}",
        "zh_TW": "  顯示名稱: {display_name}",
        "ja": "  表示名: {display_name}",
        "ko": "  표시 이름: {display_name}",
        "de": "  Anzeigename: {display_name}",
        "fr": "  Nom d'affichage : {display_name}",
        "ru": "  Отображаемое имя: {display_name}",
        "es": "  Nombre para mostrar: {display_name}",
    },
    "wizard_confirm_icon": {
        "en": "  Icon: {icon_path}",
        "zh": "  图标: {icon_path}",
        "zh_TW": "  圖示: {icon_path}",
        "ja": "  アイコン: {icon_path}",
        "ko": "  아이콘: {icon_path}",
        "de": "  Symbol: {icon_path}",
        "fr": "  Icône : {icon_path}",
        "ru": "  Значок: {icon_path}",
        "es": "  Icono: {icon_path}",
    },
    "wizard_confirm_target": {
        "en": "  Target: {dest_path}",
        "zh": "  目标: {dest_path}",
        "zh_TW": "  目標: {dest_path}",
        "ja": "  出力先: {dest_path}",
        "ko": "  대상: {dest_path}",
        "de": "  Ziel: {dest_path}",
        "fr": "  Cible : {dest_path}",
        "ru": "  Назначение: {dest_path}",
        "es": "  Destino: {dest_path}",
    },
    "wizard_confirm_data_dir": {
        "en": "  Data Dir: {data_dir}",
        "zh": "  数据目录: {data_dir}",
        "zh_TW": "  資料目錄: {data_dir}",
        "ja": "  データディレクトリ: {data_dir}",
        "ko": "  데이터 디렉토리: {data_dir}",
        "de": "  Datenverzeichnis: {data_dir}",
        "fr": "  Dossier de données : {data_dir}",
        "ru": "  Каталог данных: {data_dir}",
        "es": "  Directorio de datos: {data_dir}",
    },

    "wizard_confirm_strategy": {
        "en": "  Strategy: {strategy}",
        "zh": "  策略: {strategy}",
        "zh_TW": "  策略: {strategy}",
        "ja": "  戦略: {strategy}",
        "ko": "  전략: {strategy}",
        "de": "  Strategie: {strategy}",
        "fr": "  Stratégie : {strategy}",
        "ru": "  Стратегия: {strategy}",
        "es": "  Estrategia: {strategy}",
    },
    "wizard_proxy_configured": {
        "en": "Configured",
        "zh": "已配置",
        "zh_TW": "已設定",
        "ja": "設定済み",
        "ko": "설정됨",
        "de": "Konfiguriert",
        "fr": "Configuré",
        "ru": "Настроен",
        "es": "Configurado",
    },
    "wizard_proxy_not_configured": {
        "en": "Not configured",
        "zh": "未配置",
        "zh_TW": "未設定",
        "ja": "未設定",
        "ko": "미설정",
        "de": "Nicht konfiguriert",
        "fr": "Non configuré",
        "ru": "Не настроен",
        "es": "No configurado",
    },
    "wizard_confirm_proxy": {
        "en": "  Proxy: {proxy_status}\n",
        "zh": "  代理: {proxy_status}\n",
        "zh_TW": "  代理: {proxy_status}\n",
        "ja": "  プロキシ: {proxy_status}\n",
        "ko": "  프록시: {proxy_status}\n",
        "de": "  Proxy: {proxy_status}\n",
        "fr": "  Proxy : {proxy_status}\n",
        "ru": "  Прокси: {proxy_status}\n",
        "es": "  Proxy: {proxy_status}\n",
    },
    "wizard_prompt_confirm": {
        "en": "Confirm execution",
        "zh": "确认执行",
        "zh_TW": "確認執行",
        "ja": "実行を確認",
        "ko": "실행 확인",
        "de": "Ausführung bestätigen",
        "fr": "Confirmer l'exécution",
        "ru": "Подтвердить выполнение",
        "es": "Confirmar ejecución",
    },

    # --- Common Execution Messages ---
    "starting_clone": {
        "en": "[bold green]Starting clone:[/bold green] {app_name} -> {clone_name}",
        "zh": "[bold green]开始创建分身:[/bold green] {app_name} -> {clone_name}",
        "zh_TW": "[bold green]開始建立分身:[/bold green] {app_name} -> {clone_name}",
        "ja": "[bold green]クローン作成を開始:[/bold green] {app_name} -> {clone_name}",
        "ko": "[bold green]클론 생성 시작:[/bold green] {app_name} -> {clone_name}",
        "de": "[bold green]Klonvorgang gestartet:[/bold green] {app_name} -> {clone_name}",
        "fr": "[bold green]Démarrage du clonage :[/bold green] {app_name} -> {clone_name}",
        "ru": "[bold green]Запуск клонирования:[/bold green] {app_name} -> {clone_name}",
        "es": "[bold green]Iniciando clonación:[/bold green] {app_name} -> {clone_name}",
    },
    "clone_success": {
        "en": "[bold green]Success![/bold green] Clone created at {dest_path}",
        "zh": "[bold green]成功！[/bold green] 分身创建于 {dest_path}",
        "zh_TW": "[bold green]成功！[/bold green] 分身建立於 {dest_path}",
        "ja": "[bold green]成功！[/bold green] クローンを作成しました: {dest_path}",
        "ko": "[bold green]성공！[/bold green] 클론이 생성되었습니다: {dest_path}",
        "de": "[bold green]Erfolg![/bold green] Klon erstellt unter {dest_path}",
        "fr": "[bold green]Succès ![/bold green] Clone créé à l'emplacement {dest_path}",
        "ru": "[bold green]Успешно![/bold green] Клон создан в {dest_path}",
        "es": "[bold green]¡Éxito![/bold green] Clon creado en {dest_path}",
    },
    "clone_error": {
        "en": "[bold red]Error:[/bold red] {error}",
        "zh": "[bold red]错误:[/bold red] {error}",
        "zh_TW": "[bold red]錯誤:[/bold red] {error}",
        "ja": "[bold red]エラー:[/bold red] {error}",
        "ko": "[bold red]오류:[/bold red] {error}",
        "de": "[bold red]Fehler:[/bold red] {error}",
        "fr": "[bold red]Erreur :[/bold red] {error}",
        "ru": "[bold red]Ошибка:[/bold red] {error}",
        "es": "[bold red]Error:[/bold red] {error}",
    },
    "clone_err_icon_icns": {
        "en": "[bold red]Error:[/bold red] --icon must be a .icns file.",
        "zh": "[bold red]错误:[/bold red] --icon 必须是 .icns 文件。",
        "zh_TW": "[bold red]錯誤:[/bold red] --icon 必須是 .icns 檔案。",
        "ja": "[bold red]エラー:[/bold red] --icon は .icns ファイルである必要があります。",
        "ko": "[bold red]오류:[/bold red] --icon 은 .icns 파일이어야 합니다.",
        "de": "[bold red]Fehler:[/bold red] --icon muss eine .icns-Datei sein.",
        "fr": "[bold red]Erreur :[/bold red] --icon doit être un fichier .icns.",
        "ru": "[bold red]Ошибка:[/bold red] --icon должен быть файлом .icns.",
        "es": "[bold red]Error:[/bold red] --icon debe ser un archivo .icns.",
    },
    "clone_err_data_dir_not_supported": {
        "en": "[bold red]Error:[/bold red] Application '{app_name}' does not support custom data directory.",
        "zh": "[bold red]错误:[/bold red] 应用 '{app_name}' 不支持自定义数据目录。",
        "zh_TW": "[bold red]錯誤:[/bold red] 應用程式 '{app_name}' 不支援自訂資料目錄。",
        "ja": "[bold red]エラー:[/bold red] アプリ '{app_name}' はカスタムデータディレクトリに対応していません。",
        "ko": "[bold red]오류:[/bold red] 앱 '{app_name}'은(는) 사용자 정의 데이터 디렉토리를 지원하지 않습니다.",
        "de": "[bold red]Fehler:[/bold red] Anwendung '{app_name}' unterstützt kein benutzerdefiniertes Datenverzeichnis.",
        "fr": "[bold red]Erreur :[/bold red] L'application '{app_name}' ne prend pas en charge de dossier de données personnalisé.",
        "ru": "[bold red]Ошибка:[/bold red] Приложение '{app_name}' не поддерживает пользовательский каталог данных.",
        "es": "[bold red]Error:[/bold red] La aplicación '{app_name}' no admite un directorio de datos personalizado.",
    },

    "clone_no_recipe_found": {
        "en": "[yellow]No pre-configured recipe found for '{bundle_id}'.[/yellow]",
        "zh": "[yellow]未找到 '{bundle_id}' 的预设配方。[/yellow]",
        "zh_TW": "[yellow]未找到 '{bundle_id}' 的預設配方。[/yellow]",
        "ja": "[yellow]'{bundle_id}' のプリセットレシピが見つかりません。[/yellow]",
        "ko": "[yellow]'{bundle_id}'에 대한 사전 설정 레시피를 찾을 수 없습니다.[/yellow]",
        "de": "[yellow]Kein vordefiniertes Rezept für '{bundle_id}' gefunden.[/yellow]",
        "fr": "[yellow]Aucune recette prédéfinie trouvée pour '{bundle_id}'.[/yellow]",
        "ru": "[yellow]Готовый рецепт для '{bundle_id}' не найден.[/yellow]",
        "es": "[yellow]No se encontró una receta predefinida para '{bundle_id}'.[/yellow]",
    },
    "clone_probing": {
        "en": "[cyan]Probing application architecture and entitlements...[/cyan]",
        "zh": "[cyan]正在探测应用架构与沙盒权限...[/cyan]",
        "zh_TW": "[cyan]正在探測應用程式架構與沙盒權限...[/cyan]",
        "ja": "[cyan]アプリのアーキテクチャとサンドボックス権限を解析中...[/cyan]",
        "ko": "[cyan]앱 아키텍처 및 샌드박스 권한을 감지하는 중...[/cyan]",
        "de": "[cyan]Anwendungsarchitektur und Sandbox-Berechtigungen werden analysiert...[/cyan]",
        "fr": "[cyan]Analyse de l'architecture et des privilèges sandbox...[/cyan]",
        "ru": "[cyan]Анализ архитектуры и прав песочницы...[/cyan]",
        "es": "[cyan]Analizando arquitectura de la aplicación y permisos de sandbox...[/cyan]",
    },
    "clone_probed_strategy": {
        "en": "[cyan]Probed Strategy:[/cyan] [bold]{strategy}[/bold] (Sandbox: {sandbox})",
        "zh": "[cyan]探测策略:[/cyan] [bold]{strategy}[/bold] (沙盒: {sandbox})",
        "zh_TW": "[cyan]探測策略:[/cyan] [bold]{strategy}[/bold] (沙盒: {sandbox})",
        "ja": "[cyan]推奨戦略:[/cyan] [bold]{strategy}[/bold] (サンドボックス: {sandbox})",
        "ko": "[cyan]추천 전략:[/cyan] [bold]{strategy}[/bold] (샌드박스: {sandbox})",
        "de": "[cyan]Empfohlene Strategie:[/cyan] [bold]{strategy}[/bold] (Sandbox: {sandbox})",
        "fr": "[cyan]Stratégie recommandée :[/cyan] [bold]{strategy}[/bold] (Sandbox : {sandbox})",
        "ru": "[cyan]Рекомендуемая стратегия:[/cyan] [bold]{strategy}[/bold] (Песочница: {sandbox})",
        "es": "[cyan]Estrategia recomendada:[/cyan] [bold]{strategy}[/bold] (Sandbox: {sandbox})",
    },

    # --- Doctor Command ---
    "doctor_running_checks": {
        "en": "[bold]Running environment checks:[/bold]",
        "zh": "[bold]正在执行环境检查:[/bold]",
        "zh_TW": "[bold]正在執行環境檢查:[/bold]",
        "ja": "[bold]環境チェックを実行中:[/bold]",
        "ko": "[bold]환경 검사를 실행하는 중:[/bold]",
        "de": "[bold]Umgebungsprüfung läuft:[/bold]",
        "fr": "[bold]Exécution des vérifications d'environnement :[/bold]",
        "ru": "[bold]Выполнение проверки окружения:[/bold]",
        "es": "[bold]Ejecutando comprobaciones de entorno:[/bold]",
    },
    "doctor_missing": {
        "en": "Missing! Run 'xcode-select --install'",
        "zh": "缺失！请运行 'xcode-select --install'",
        "zh_TW": "缺失！請執行 'xcode-select --install'",
        "ja": "見つかりません！ 'xcode-select --install' を実行してください",
        "ko": "누락됨! 'xcode-select --install'을 실행하세요",
        "de": "Fehlt! Bitte 'xcode-select --install' ausführen",
        "fr": "Manquant ! Exécutez 'xcode-select --install'",
        "ru": "Отсутствует! Выполните 'xcode-select --install'",
        "es": "¡Falta! Ejecute 'xcode-select --install'",
    },

    # --- List Command ---
    "list_no_clones": {
        "en": "[yellow]No clones found.[/yellow]",
        "zh": "[yellow]未找到任何分身应用。[/yellow]",
        "zh_TW": "[yellow]未找到任何分身應用程式。[/yellow]",
        "ja": "[yellow]クローンされたアプリが見つかりません。[/yellow]",
        "ko": "[yellow]생성된 클론이 없습니다.[/yellow]",
        "de": "[yellow]Keine Klone gefunden.[/yellow]",
        "fr": "[yellow]Aucun clone trouvé.[/yellow]",
        "ru": "[yellow]Клоны не найдены.[/yellow]",
        "es": "[yellow]No se encontraron clones.[/yellow]",
    },
    "list_col_name": {
        "en": "Name",
        "zh": "名称",
        "zh_TW": "名稱",
        "ja": "名前",
        "ko": "이름",
        "de": "Name",
        "fr": "Nom",
        "ru": "Имя",
        "es": "Nombre",
    },
    "list_col_source_app": {
        "en": "Source App",
        "zh": "原 APP",
        "zh_TW": "原始 APP",
        "ja": "元アプリ",
        "ko": "원본 앱",
        "de": "Quell-App",
        "fr": "App source",
        "ru": "Исходное приложение",
        "es": "App original",
    },
    "list_col_bundle_id": {
        "en": "Bundle ID",
        "zh": "Bundle ID",
        "zh_TW": "Bundle ID",
        "ja": "Bundle ID",
        "ko": "Bundle ID",
        "de": "Bundle ID",
        "fr": "Bundle ID",
        "ru": "Bundle ID",
        "es": "Bundle ID",
    },
    "list_col_strategy": {
        "en": "Strategy",
        "zh": "策略",
        "zh_TW": "策略",
        "ja": "戦略",
        "ko": "전략",
        "de": "Strategie",
        "fr": "Stratégie",
        "ru": "Стратегия",
        "es": "Estrategia",
    },
    "list_col_created_at": {
        "en": "Created At",
        "zh": "创建时间",
        "zh_TW": "建立時間",
        "ja": "作成日時",
        "ko": "생성 시간",
        "de": "Erstellt am",
        "fr": "Date de création",
        "ru": "Дата создания",
        "es": "Fecha de creación",
    },
    "list_col_proxy": {
        "en": "Proxy",
        "zh": "代理",
        "zh_TW": "代理",
        "ja": "プロキシ",
        "ko": "프록시",
        "de": "Proxy",
        "fr": "Proxy",
        "ru": "Прокси",
        "es": "Proxy",
    },
    "list_proxy_disabled": {
        "en": "Disabled",
        "zh": "未开启",
        "zh_TW": "未啟用",
        "ja": "無効",
        "ko": "비활성",
        "de": "Deaktiviert",
        "fr": "Désactivé",
        "ru": "Отключено",
        "es": "Desactivado",
    },

    # --- Remove Command ---
    "remove_err_not_found": {
        "en": "[red]Error:[/red] Clone '{clone_name}' not found.",
        "zh": "[red]错误:[/red] 未找到分身 '{clone_name}'。",
        "zh_TW": "[red]錯誤:[/red] 未找到分身 '{clone_name}'。",
        "ja": "[red]エラー:[/red] クローン '{clone_name}' が見つかりません。",
        "ko": "[red]오류:[/red] 클론 '{clone_name}'을(를) 찾을 수 없습니다.",
        "de": "[red]Fehler:[/red] Klon '{clone_name}' nicht gefunden.",
        "fr": "[red]Erreur :[/red] Clone '{clone_name}' introuvable.",
        "ru": "[red]Ошибка:[/red] Клон '{clone_name}' не найден.",
        "es": "[red]Error:[/red] Clon '{clone_name}' no encontrado.",
    },
    "remove_confirm_data": {
        "en": "Also delete data directory {data_dir}? This is irreversible.",
        "zh": "是否同时删除数据目录 {data_dir}？此操作不可逆。",
        "zh_TW": "是否同時刪除資料目錄 {data_dir}？此操作不可逆。",
        "ja": "データディレクトリ {data_dir} も削除しますか？この操作は取り消せません。",
        "ko": "데이터 디렉토리 {data_dir}도 삭제하시겠습니까? 이 작업은 취소할 수 없습니다.",
        "de": "Datenverzeichnis {data_dir} ebenfalls löschen? Dies kann nicht rückgängig gemacht werden.",
        "fr": "Supprimer également le dossier de données {data_dir} ? Cette action est irréversible.",
        "ru": "Также удалить каталог данных {data_dir}? Это действие необратимо.",
        "es": "¿Eliminar también el directorio de datos {data_dir}? Esta acción es irreversible.",
    },
    "remove_prompt_delete_data": {
        "en": "Also delete data directory {data_dir}?",
        "zh": "是否同时删除数据目录 {data_dir}？",
        "zh_TW": "是否同時刪除資料目錄 {data_dir}？",
        "ja": "データディレクトリ {data_dir} も削除しますか？",
        "ko": "데이터 디렉토리 {data_dir}도 삭제하시겠습니까?",
        "de": "Datenverzeichnis {data_dir} ebenfalls löschen?",
        "fr": "Supprimer également le dossier de données {data_dir} ?",
        "ru": "Также удалить каталог данных {data_dir}?",
        "es": "¿Eliminar también el directorio de datos {data_dir}?",
    },

    "remove_success": {
        "en": "[bold green]Success![/bold green] Removed clone '{clone_name}'",
        "zh": "[bold green]成功！[/bold green] 已删除分身 '{clone_name}'",
        "zh_TW": "[bold green]成功！[/bold green] 已刪除分身 '{clone_name}'",
        "ja": "[bold green]成功！[/bold green] クローン '{clone_name}' を削除しました",
        "ko": "[bold green]성공！[/bold green] 클론 '{clone_name}'이(가) 삭제되었습니다",
        "de": "[bold green]Erfolg![/bold green] Klon '{clone_name}' entfernt",
        "fr": "[bold green]Succès ![/bold green] Clone '{clone_name}' supprimé",
        "ru": "[bold green]Успешно![/bold green] Клон '{clone_name}' удален",
        "es": "[bold green]¡Éxito![/bold green] Clon '{clone_name}' eliminado",
    },

    # --- Update Command ---
    "update_err_not_found": {
        "en": "[red]Error:[/red] Clone '{clone_name}' not found.",
        "zh": "[red]错误:[/red] 未找到分身 '{clone_name}'。",
        "zh_TW": "[red]錯誤:[/red] 未找到分身 '{clone_name}'。",
        "ja": "[red]エラー:[/red] クローン '{clone_name}' が見つかりません。",
        "ko": "[red]오류:[/red] 클론 '{clone_name}'을(를) 찾을 수 없습니다.",
        "de": "[red]Fehler:[/red] Klon '{clone_name}' nicht gefunden.",
        "fr": "[red]Erreur :[/red] Clone '{clone_name}' introuvable.",
        "ru": "[red]Ошибка:[/red] Клон '{clone_name}' не найден.",
        "es": "[red]Error:[/red] Clon '{clone_name}' no encontrado.",
    },
    "update_err_source_not_found": {
        "en": "[bold red]Error:[/bold red] Source app not found at '{source_path}'",
        "zh": "[bold red]错误:[/bold red] 未在 '{source_path}' 找到源应用",
        "zh_TW": "[bold red]錯誤:[/bold red] 未在 '{source_path}' 找到來源應用程式",
        "ja": "[bold red]エラー:[/bold red] '{source_path}' に元のアプリが見つかりません",
        "ko": "[bold red]오류:[/bold red] '{source_path}'에서 원본 앱을 찾을 수 없습니다",
        "de": "[bold red]Fehler:[/bold red] Quell-App unter '{source_path}' nicht gefunden",
        "fr": "[bold red]Erreur :[/bold red] Application source introuvable à '{source_path}'",
        "ru": "[bold red]Ошибка:[/bold red] Исходное приложение не найдено в '{source_path}'",
        "es": "[bold red]Error:[/bold red] Aplicación de origen no encontrada en '{source_path}'",
    },
    "update_starting": {
        "en": "[bold]Updating {clone_name}...[/bold]",
        "zh": "[bold]正在更新 {clone_name}...[/bold]",
        "zh_TW": "[bold]正在更新 {clone_name}...[/bold]",
        "ja": "[bold]{clone_name} を更新中...[/bold]",
        "ko": "[bold]{clone_name} 업데이트 중...[/bold]",
        "de": "[bold]{clone_name} wird aktualisiert...[/bold]",
        "fr": "[bold]Mise à jour de {clone_name}...[/bold]",
        "ru": "[bold]Обновление {clone_name}...[/bold]",
        "es": "[bold]Actualizando {clone_name}...[/bold]",
    },
    "update_success": {
        "en": "[bold green]Success![/bold green] Updated {clone_name}",
        "zh": "[bold green]成功！[/bold green] 已更新 {clone_name}",
        "zh_TW": "[bold green]成功！[/bold green] 已更新 {clone_name}",
        "ja": "[bold green]成功！[/bold green] {clone_name} を更新しました",
        "ko": "[bold green]성공！[/bold green] {clone_name} 업데이트 완료",
        "de": "[bold green]Erfolg![/bold green] {clone_name} aktualisiert",
        "fr": "[bold green]Succès ![/bold green] {clone_name} mis à jour",
        "ru": "[bold green]Успешно![/bold green] {clone_name} обновлен",
        "es": "[bold green]¡Éxito![/bold green] {clone_name} actualizado",
    },

    # --- Probe Command ---
    "probe_err_invalid_app": {
        "en": "[bold red]Error:[/bold red] '{app_path}' is not a valid macOS .app bundle.",
        "zh": "[bold red]错误:[/bold red] '{app_path}' 不是有效的 macOS .app 应用程序。",
        "zh_TW": "[bold red]錯誤:[/bold red] '{app_path}' 不是有效的 macOS .app 應用程式。",
        "ja": "[bold red]エラー:[/bold red] '{app_path}' は有効な macOS .app バンドルではありません。",
        "ko": "[bold red]오류:[/bold red] '{app_path}'은(는) 올바른 macOS .app 번들이 아닙니다.",
        "de": "[bold red]Fehler:[/bold red] '{app_path}' ist kein gültiges macOS .app-Paket.",
        "fr": "[bold red]Erreur :[/bold red] '{app_path}' n'est pas un paquet .app macOS valide.",
        "ru": "[bold red]Ошибка:[/bold red] '{app_path}' не является корректным пакетом .app macOS.",
        "es": "[bold red]Error:[/bold red] '{app_path}' no es un paquete .app válido de macOS.",
    },
    "probe_err_failed": {
        "en": "[bold red]Error during probing:[/bold red] {error}",
        "zh": "[bold red]探测应用时出错:[/bold red] {error}",
        "zh_TW": "[bold red]探測應用程式時發生錯誤:[/bold red] {error}",
        "ja": "[bold red]解析中にエラーが発生しました:[/bold red] {error}",
        "ko": "[bold red]분석 중 오류 발생:[/bold red] {error}",
        "de": "[bold red]Fehler bei der Analyse:[/bold red] {error}",
        "fr": "[bold red]Erreur lors de l'analyse :[/bold red] {error}",
        "ru": "[bold red]Ошибка при анализе:[/bold red] {error}",
        "es": "[bold red]Error durante el análisis:[/bold red] {error}",
    },
    "probe_title": {
        "en": "🔍 [bold]ATBClone Deep Application Probe[/bold]",
        "zh": "🔍 [bold]ATBClone 深度应用探测[/bold]",
        "zh_TW": "🔍 [bold]ATBClone 深度應用程式探測[/bold]",
        "ja": "🔍 [bold]ATBClone アプリケーション詳細解析[/bold]",
        "ko": "🔍 [bold]ATBClone 앱 정밀 분석[/bold]",
        "de": "🔍 [bold]ATBClone Anwendungs-Tiefenanalyse[/bold]",
        "fr": "🔍 [bold]Analyse approfondie de l'application ATBClone[/bold]",
        "ru": "🔍 [bold]Глубокий анализ приложения ATBClone[/bold]",
        "es": "🔍 [bold]Análisis profundo de aplicaciones ATBClone[/bold]",
    },
    "probe_row_app_name": {
        "en": "App Name",
        "zh": "应用名称",
        "zh_TW": "應用程式名稱",
        "ja": "アプリ名",
        "ko": "앱 이름",
        "de": "App-Name",
        "fr": "Nom de l'application",
        "ru": "Имя приложения",
        "es": "Nombre de la app",
    },
    "probe_row_bundle_id": {
        "en": "Bundle ID",
        "zh": "Bundle ID",
        "zh_TW": "Bundle ID",
        "ja": "Bundle ID",
        "ko": "Bundle ID",
        "de": "Bundle ID",
        "fr": "Bundle ID",
        "ru": "Bundle ID",
        "es": "Bundle ID",
    },
    "probe_row_executable": {
        "en": "Executable",
        "zh": "可执行文件",
        "zh_TW": "可執行檔",
        "ja": "実行可能ファイル",
        "ko": "실행 파일",
        "de": "Ausführbare Datei",
        "fr": "Exécutable",
        "ru": "Исполняемый файл",
        "es": "Ejecutable",
    },
    "probe_row_sandbox": {
        "en": "Sandbox Status",
        "zh": "沙盒状态",
        "zh_TW": "沙盒狀態",
        "ja": "サンドボックス状態",
        "ko": "샌드박스 상태",
        "de": "Sandbox-Status",
        "fr": "État du Sandbox",
        "ru": "Статус песочницы",
        "es": "Estado del Sandbox",
    },
    "probe_row_frameworks": {
        "en": "Frameworks",
        "zh": "检测框架",
        "zh_TW": "偵測框架",
        "ja": "検出フレームワーク",
        "ko": "감지된 프레임워크",
        "de": "Erkannte Frameworks",
        "fr": "Frameworks détectés",
        "ru": "Обнаруженные фреймворки",
        "es": "Frameworks detectados",
    },
    "probe_row_strategy": {
        "en": "Recommended Strategy",
        "zh": "推荐策略",
        "zh_TW": "推薦策略",
        "ja": "推奨戦略",
        "ko": "추천 전략",
        "de": "Empfohlene Strategie",
        "fr": "Stratégie recommandée",
        "ru": "Рекомендуемая стратегия",
        "es": "Estrategia recomendada",
    },
    "probe_row_reason": {
        "en": "Analysis Notes",
        "zh": "分析说明",
        "zh_TW": "分析說明",
        "ja": "解析説明",
        "ko": "분석 설명",
        "de": "Anmerkungen zur Analyse",
        "fr": "Remarques d'analyse",
        "ru": "Примечания к анализу",
        "es": "Notas de análisis",
    },
    "probe_yaml_header": {
        "en": "\n[bold]--- Generated Recipe YAML ---[/bold]",
        "zh": "\n[bold]--- 生成的 Recipe YAML ---[/bold]",
        "zh_TW": "\n[bold]--- 產生的 Recipe YAML ---[/bold]",
        "ja": "\n[bold]--- 生成された Recipe YAML ---[/bold]",
        "ko": "\n[bold]--- 생성된 Recipe YAML ---[/bold]",
        "de": "\n[bold]--- Generiertes Recipe YAML ---[/bold]",
        "fr": "\n[bold]--- Recipe YAML généré ---[/bold]",
        "ru": "\n[bold]--- Сгенерированный Recipe YAML ---[/bold]",
        "es": "\n[bold]--- Recipe YAML generado ---[/bold]",
    },
    "probe_saved_to": {
        "en": "[bold green]✔ Saved recipe to:[/bold green] {path}",
        "zh": "[bold green]✔ 已保存配方至:[/bold green] {path}",
        "zh_TW": "[bold green]✔ 已儲存配方至:[/bold green] {path}",
        "ja": "[bold green]✔ レシピを保存しました:[/bold green] {path}",
        "ko": "[bold green]✔ 레시피가 저장되었습니다:[/bold green] {path}",
        "de": "[bold green]✔ Rezept gespeichert unter:[/bold green] {path}",
        "fr": "[bold green]✔ Recette enregistrée sous :[/bold green] {path}",
        "ru": "[bold green]✔ Рецепт сохранен в:[/bold green] {path}",
        "es": "[bold green]✔ Receta guardada en:[/bold green] {path}",
    },

    # --- Recipe Command ---
    "recipe_col_bundle_id": {
        "en": "Bundle ID",
        "zh": "Bundle ID",
        "zh_TW": "Bundle ID",
        "ja": "Bundle ID",
        "ko": "Bundle ID",
        "de": "Bundle ID",
        "fr": "Bundle ID",
        "ru": "Bundle ID",
        "es": "Bundle ID",
    },
    "recipe_col_app_name": {
        "en": "App Name",
        "zh": "应用名称",
        "zh_TW": "應用程式名稱",
        "ja": "アプリ名",
        "ko": "앱 이름",
        "de": "App-Name",
        "fr": "Nom de l'application",
        "ru": "Имя приложения",
        "es": "Nombre de la app",
    },
    "recipe_col_strategy": {
        "en": "Strategy",
        "zh": "策略",
        "zh_TW": "策略",
        "ja": "戦略",
        "ko": "전략",
        "de": "Strategie",
        "fr": "Stratégie",
        "ru": "Стратегия",
        "es": "Estrategia",
    },
    "recipe_col_strip_sandbox": {
        "en": "Strip Sandbox",
        "zh": "解除沙盒",
        "zh_TW": "解除沙盒",
        "ja": "サンドボックス解除",
        "ko": "샌드박스 해제",
        "de": "Sandbox entfernen",
        "fr": "Retirer le sandbox",
        "ru": "Удалить песочницу",
        "es": "Eliminar Sandbox",
    },
    "recipe_local_override": {
        "en": "[yellow](local override)[/yellow]",
        "zh": "[yellow](本地覆盖)[/yellow]",
        "zh_TW": "[yellow](本機覆寫)[/yellow]",
        "ja": "[yellow](ローカル上書き)[/yellow]",
        "ko": "[yellow](로컬 재정의)[/yellow]",
        "de": "[yellow](Lokales Override)[/yellow]",
        "fr": "[yellow](Remplacement local)[/yellow]",
        "ru": "[yellow](Локальное переопределение)[/yellow]",
        "es": "[yellow](Sobrescritura local)[/yellow]",
    },
    "recipe_err_not_found": {
        "en": "[red]Error:[/red] Recipe for '{bundle_id}' not found.",
        "zh": "[red]错误:[/red] 未找到 '{bundle_id}' 的配方。",
        "zh_TW": "[red]錯誤:[/red] 未找到 '{bundle_id}' 的配方。",
        "ja": "[red]エラー:[/red] '{bundle_id}' のレシピが見つかりません。",
        "ko": "[red]오류:[/red] '{bundle_id}'의 레시피를 찾을 수 없습니다.",
        "de": "[red]Fehler:[/red] Rezept für '{bundle_id}' nicht gefunden.",
        "fr": "[red]Erreur :[/red] Recette pour '{bundle_id}' introuvable.",
        "ru": "[red]Ошибка:[/red] Рецепт для '{bundle_id}' не найден.",
        "es": "[red]Error:[/red] Receta para '{bundle_id}' no encontrada.",
    },

    # --- Version Command ---
    "version_panel_title": {
        "en": "[bold green]ATBClone System Information[/bold green]",
        "zh": "[bold green]ATBClone 系统信息[/bold green]",
        "zh_TW": "[bold green]ATBClone 系統資訊[/bold green]",
        "ja": "[bold green]ATBClone システム情報[/bold green]",
        "ko": "[bold green]ATBClone 시스템 정보[/bold green]",
        "de": "[bold green]ATBClone Systeminformationen[/bold green]",
        "fr": "[bold green]Informations système ATBClone[/bold green]",
        "ru": "[bold green]Системная информация ATBClone[/bold green]",
        "es": "[bold green]Información del sistema ATBClone[/bold green]",
    },
    "version_row_version": {
        "en": "ATBClone Version",
        "zh": "ATBClone 版本",
        "zh_TW": "ATBClone 版本",
        "ja": "ATBClone バージョン",
        "ko": "ATBClone 버전",
        "de": "ATBClone Version",
        "fr": "Version d'ATBClone",
        "ru": "Версия ATBClone",
        "es": "Versión de ATBClone",
    },
    "version_row_python": {
        "en": "Python Runtime",
        "zh": "Python 运行时",
        "zh_TW": "Python 執行時期",
        "ja": "Python ランタイム",
        "ko": "Python 런타임",
        "de": "Python-Laufzeit",
        "fr": "Runtime Python",
        "ru": "Среда Python",
        "es": "Entorno de ejecución Python",
    },
    "version_row_platform": {
        "en": "Platform",
        "zh": "操作系统平台",
        "zh_TW": "作業系統平台",
        "ja": "プラットフォーム",
        "ko": "운영체제 플랫폼",
        "de": "Betriebssystem-Plattform",
        "fr": "Plateforme système",
        "ru": "Платформа ОС",
        "es": "Plataforma del SO",
    },
    "version_row_executable": {
        "en": "Executable",
        "zh": "可执行文件路径",
        "zh_TW": "執行檔路徑",
        "ja": "実行可能ファイルパス",
        "ko": "실행 파일 경로",
        "de": "Pfad der Binärdatei",
        "fr": "Chemin de l'exécutable",
        "ru": "Путь к исполняемому файлу",
        "es": "Ruta del ejecutable",
    },
    "version_row_state": {
        "en": "State Storage",
        "zh": "状态存储文件",
        "zh_TW": "狀態儲存檔案",
        "ja": "状態ファイル",
        "ko": "상태 저장 파일",
        "de": "Statusdatei",
        "fr": "Fichier d'état",
        "ru": "Файл состояния",
        "es": "Archivo de estado",
    },
    "version_row_data": {
        "en": "Data Directory",
        "zh": "数据存储目录",
        "zh_TW": "資料儲存目錄",
        "ja": "データディレクトリ",
        "ko": "데이터 디렉토리",
        "de": "Datenverzeichnis",
        "fr": "Dossier de données",
        "ru": "Каталог данных",
        "es": "Directorio de datos",
    },
}


def normalize_lang_code(raw: str | None) -> str:
    """Normalize a raw language / locale string to one of the supported codes."""
    if not raw:
        return "en"
    cleaned = raw.strip().lower().replace("-", "_")
    if not cleaned:
        return "en"

    # Traditional Chinese check
    if (
        cleaned.startswith("zh_tw")
        or cleaned.startswith("zh_hk")
        or cleaned.startswith("zh_mo")
        or cleaned.startswith("zh_hant")
        or "hant" in cleaned
    ):
        return "zh_TW"

    # Simplified Chinese check
    if cleaned.startswith("zh"):
        return "zh"

    # Other supported languages
    for prefix, target in (
        ("ja", "ja"),
        ("ko", "ko"),
        ("de", "de"),
        ("fr", "fr"),
        ("ru", "ru"),
        ("es", "es"),
        ("en", "en"),
    ):
        if cleaned.startswith(prefix):
            return target

    return "en"


def detect_system_language() -> str:
    """Detect the current macOS system language or environment preferences.

    Returns:
        One of the supported language codes: 'en', 'zh', 'zh_TW', 'ja', 'ko', 'de', 'fr', 'ru', 'es'.
    """
    # 1. Explicit user override via environment variable (highest priority)
    override = os.environ.get("ATBCLONE_LANG", "").strip()
    if override:
        return normalize_lang_code(override)

    # 2. macOS System Preferences via 'defaults read -g AppleLanguages'
    try:
        out = subprocess.check_output(
            ["defaults", "read", "-g", "AppleLanguages"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        langs = re.findall(r'"([^"]+)"|([a-zA-Z0-9_-]+)', out)
        first_lang = next((a or b for a, b in langs if (a or b) not in ("(", ")", "")), "")
        if first_lang:
            norm = normalize_lang_code(first_lang)
            if norm != "en" or first_lang.lower().startswith("en"):
                return norm
    except Exception:
        pass

    # 3. macOS AppleLocale
    try:
        out = subprocess.check_output(
            ["defaults", "read", "-g", "AppleLocale"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            norm = normalize_lang_code(out)
            if norm != "en" or out.lower().startswith("en"):
                return norm
    except Exception:
        pass

    # 4. Standard environment variables (LC_ALL, LC_MESSAGES, LANG)
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var, "").strip()
        if val:
            norm = normalize_lang_code(val)
            if norm != "en" or val.lower().startswith("en"):
                return norm

    # Default fallback to English
    return "en"


def get_language() -> str:
    """Get currently active language."""
    global _current_lang
    if _current_lang is not None:
        return _current_lang

    # If ATBCLONE_LANG env is set, use it
    if "ATBCLONE_LANG" in os.environ:
        override = os.environ.get("ATBCLONE_LANG", "").strip()
        if override:
            return normalize_lang_code(override)

    return detect_system_language()


def set_language(lang: str | None) -> None:
    """Explicitly set or reset the active language ('zh', 'zh_TW', 'ja', 'ko', 'de', 'fr', 'ru', 'es', 'en', or None for auto)."""
    global _current_lang
    if lang is None:
        _current_lang = None
    else:
        _current_lang = normalize_lang_code(lang)


def is_chinese() -> bool:
    """Check if the active language is Chinese (Simplified or Traditional)."""
    return get_language() in ("zh", "zh_TW")


def t(key: str, **kwargs: Any) -> str:
    """Translate a message key to the current language with optional keyword formatting."""
    lang = get_language()
    msg_dict = MESSAGES.get(key)
    if not msg_dict:
        return key.format(**kwargs) if kwargs else key

    template = (
        msg_dict.get(lang)
        or (msg_dict.get("zh") if lang == "zh_TW" else None)
        or msg_dict.get("en")
        or msg_dict.get("zh")
        or key
    )
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
