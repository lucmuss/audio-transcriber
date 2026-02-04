"""
Internationalization (i18n) module for Audio Transcriber GUI.

Supports multiple languages with English as fallback.
"""

from typing import Any, Dict

# Language names with native representation
LANGUAGE_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "pt": "Português",
    "ja": "日本語",
    "zh": "中文",
    "it": "Italiano",
    "nl": "Nederlands",
    "ru": "Русский",
    "ko": "한국어",
    "ar": "العربية",
}

# Translation dictionaries for each language
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # English (Complete)
    "en": {
        # Window
        "window_title": "Audio Transcriber",
        "version": "Version",
        # Tabs
        "tab_main": "📁 Main Settings",
        "tab_api": "🔌 API Configuration",
        "tab_advanced": "⚙️ Advanced",
        "tab_transcription": "📝 Transcription",
        # Main Tab
        "input": "Input",
        "audio_file_or_folder": "Audio File or Folder:",
        "choose_file": "Choose File",
        "choose_folder": "Choose Folder",
        "output": "Output",
        "transcription_folder": "Transcription Folder:",
        "segment_folder": "Segment Folder:",
        "output_format": "Output Format:",
        "browse": "Browse",
        "behavior": "Behavior",
        "keep_segments": "Keep segments",
        "skip_existing": "Skip existing files",
        "verbose_logging": "Verbose logging",
        # API Tab
        "api_settings": "API Settings",
        "api_key_label": "API Key:",
        "base_url_label": "Base URL:",
        "model_label": "Model:",
        "show_password": "Show",
        "hide_password": "Hide",
        "provider_examples": "ℹ️ Provider Examples",
        "start_transcription_btn": "▶ Start Transcription",
        "stop_btn": "⏹ Stop",
        "clear_log_btn": "🗑 Clear Log",
        "quit_btn": "❌ Quit",
        # Advanced Tab
        "segmentation_params": "Segmentation Parameters",
        "segment_length_label": "Segment Length (seconds):",
        "overlap_label": "Overlap (seconds):",
        "performance": "Performance",
        "parallel_transcriptions_label": "Parallel Transcriptions:",
        # Transcription Tab
        "transcription_settings": "Transcription Settings",
        "language_iso_label": "Language (ISO-639-1):",
        "language_hint": "(e.g. 'en', 'de', empty for auto-detect)",
        "auto_detect_language": "Auto-detect language",
        "temperature_label": "Temperature (0.0-1.0):",
        "context_prompt_label": "Context Prompt:",
        "prompt_tip": "Tip: Names, technical terms for better accuracy",
        # Progress
        "progress": "Progress",
        "start_transcription": "▶ Start Transcription",
        "stop": "⏹ Stop",
        "clear_log": "🗑 Clear Log",
        "quit": "❌ Quit",
        # Language
        "language_selector": "Language:",
        # Messages
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "success": "Success",
        "finished": "Finished",
        "error_no_input": "Please select an audio file or folder.",
        "error_no_api_key": "Please enter an API key.",
        "error_path_not_exists": "Path does not exist: {path}",
        "warning_already_processing": "Transcription is already running!",
        "warning_no_files_found": "No audio files found!",
        "started": "Audio Transcriber started",
        "found_files": "📁 Found: {count} audio file(s)",
        "processing_file": "[{current}/{total}] Processing: {filename}",
        "success_file": "✅ Success: {output}",
        "skipped_file": "⊘ Skipped: already exists",
        "error_file": "❌ Error: {error}",
        "exception": "❌ Exception: {error}",
        "stopped": "⏹ Transcription stopped!",
        "critical_error": "❌ Critical error: {error}",
        "summary": "SUMMARY",
        "successful": "✅ Successful: {count}",
        "failed": "❌ Failed: {count}",
        "finished_success": "Transcription completed!\n{count} file(s) successfully processed.",
        "finished_with_errors": "Transcription completed with {count} error(s).",
        "stopping": "⏹ Stopping transcription...",
        # Dialog titles
        "choose_audio_file": "Choose Audio File",
        "choose_audio_folder": "Choose Audio Folder",
        "choose_output_folder": "Choose Output Folder",
        "choose_segment_folder": "Choose Segment Folder",
    },
    # German (Complete)
    "de": {
        # Window
        "window_title": "Audio Transcriber",
        "version": "Version",
        # Tabs
        "tab_main": "📁 Haupteinstellungen",
        "tab_api": "🔌 API Konfiguration",
        "tab_advanced": "⚙️ Erweitert",
        "tab_transcription": "📝 Transkription",
        # Main Tab
        "input": "Eingabe",
        "audio_file_or_folder": "Audio-Datei oder Ordner:",
        "choose_file": "Datei wählen",
        "choose_folder": "Ordner wählen",
        "output": "Ausgabe",
        "transcription_folder": "Transkriptions-Ordner:",
        "segment_folder": "Segment-Ordner:",
        "output_format": "Ausgabeformat:",
        "browse": "Durchsuchen",
        "behavior": "Verhalten",
        "keep_segments": "Segmente behalten",
        "skip_existing": "Existierende Dateien überspringen",
        "verbose_logging": "Verbose Logging",
        # API Tab
        "api_settings": "API Einstellungen",
        "api_key_label": "API Key:",
        "base_url_label": "Base URL:",
        "model_label": "Model:",
        "show_password": "Anzeigen",
        "hide_password": "Verbergen",
        "provider_examples": "ℹ️ Provider-Beispiele",
        "start_transcription_btn": "▶ Transkription starten",
        "stop_btn": "⏹ Stoppen",
        "clear_log_btn": "🗑 Log löschen",
        "quit_btn": "❌ Beenden",
        # Advanced Tab
        "segmentation_params": "Segmentierungs-Parameter",
        "segment_length_label": "Segment-Länge (Sekunden):",
        "overlap_label": "Überlappung (Sekunden):",
        "performance": "Performance",
        "parallel_transcriptions_label": "Parallele Transkriptionen:",
        # Transcription Tab
        "transcription_settings": "Transkriptions-Einstellungen",
        "language_iso_label": "Sprache (ISO-639-1):",
        "language_hint": "(z.B. 'en', 'de', leer für Auto-Detect)",
        "auto_detect_language": "Sprache automatisch erkennen",
        "temperature_label": "Temperature (0.0-1.0):",
        "context_prompt_label": "Kontext-Prompt:",
        "prompt_tip": "Tipp: Namen, Fachbegriffe für bessere Genauigkeit",
        # Progress
        "progress": "Fortschritt",
        "start_transcription": "▶ Transkription starten",
        "stop": "⏹ Stoppen",
        "clear_log": "🗑 Log löschen",
        "quit": "❌ Beenden",
        # Language
        "language_selector": "Sprache:",
        # Messages
        "error": "Fehler",
        "warning": "Warnung",
        "info": "Information",
        "success": "Erfolg",
        "finished": "Fertig",
        "error_no_input": "Bitte wählen Sie eine Audio-Datei oder einen Ordner aus.",
        "error_no_api_key": "Bitte geben Sie einen API Key ein.",
        "error_path_not_exists": "Pfad existiert nicht: {path}",
        "warning_already_processing": "Transkription läuft bereits!",
        "warning_no_files_found": "Keine Audio-Dateien gefunden!",
        "started": "Audio Transcriber gestartet",
        "found_files": "📁 Gefunden: {count} Audio-Datei(en)",
        "processing_file": "[{current}/{total}] Verarbeite: {filename}",
        "success_file": "✅ Erfolgreich: {output}",
        "skipped_file": "⊘ Übersprungen: bereits vorhanden",
        "error_file": "❌ Fehler: {error}",
        "exception": "❌ Ausnahme: {error}",
        "stopped": "⏹ Transkription abgebrochen!",
        "critical_error": "❌ Kritischer Fehler: {error}",
        "summary": "ZUSAMMENFASSUNG",
        "successful": "✅ Erfolgreich: {count}",
        "failed": "❌ Fehlgeschlagen: {count}",
        "finished_success": (
            "Transkription abgeschlossen!\n{count} Datei(en) erfolgreich verarbeitet."
        ),
        "finished_with_errors": "Transkription abgeschlossen mit {count} Fehler(n).",
        "stopping": "⏹ Stoppe Transkription...",
        # Dialog titles
        "choose_audio_file": "Audio-Datei wählen",
        "choose_audio_folder": "Ordner mit Audio-Dateien wählen",
        "choose_output_folder": "Ausgabe-Ordner wählen",
        "choose_segment_folder": "Segment-Ordner wählen",
    },
    # Spanish (Partial)
    "es": {
        "window_title": "Transcriptor de Audio",
        "tab_main": "📁 Configuración Principal",
        "tab_api": "🔌 Configuración API",
        "tab_advanced": "⚙️ Avanzado",
        "tab_transcription": "📝 Transcripción",
        "input": "Entrada",
        "audio_file_or_folder": "Archivo o Carpeta de Audio:",
        "choose_file": "Elegir Archivo",
        "choose_folder": "Elegir Carpeta",
        "output": "Salida",
        "transcription_folder": "Carpeta de Transcripción:",
        "segment_folder": "Carpeta de Segmentos:",
        "output_format": "Formato de Salida:",
        "browse": "Explorar",
        "behavior": "Comportamiento",
        "keep_segments": "Mantener segmentos",
        "skip_existing": "Omitir archivos existentes",
        "verbose_logging": "Registro detallado",
        "api_key": "Clave API:",
        "model": "Modelo:",
        "show": "Mostrar",
        "hide": "Ocultar",
        "start_transcription": "▶ Iniciar Transcripción",
        "stop": "⏹ Detener",
        "clear_log": "🗑 Limpiar Registro",
        "quit": "❌ Salir",
        "language_selector": "Idioma:",
        "error": "Error",
        "warning": "Advertencia",
        "success": "Éxito",
        "error_no_input": "Por favor, seleccione un archivo o carpeta de audio.",
        "error_no_api_key": "Por favor, introduzca una clave API.",
        "warning_already_processing": "¡La transcripción ya está en curso!",
    },
    # French (Partial)
    "fr": {
        "window_title": "Transcripteur Audio",
        "tab_main": "📁 Paramètres Principaux",
        "tab_api": "🔌 Configuration API",
        "tab_advanced": "⚙️ Avancé",
        "tab_transcription": "📝 Transcription",
        "input": "Entrée",
        "audio_file_or_folder": "Fichier ou Dossier Audio:",
        "choose_file": "Choisir un Fichier",
        "choose_folder": "Choisir un Dossier",
        "output": "Sortie",
        "transcription_folder": "Dossier de Transcription:",
        "segment_folder": "Dossier de Segments:",
        "output_format": "Format de Sortie:",
        "browse": "Parcourir",
        "behavior": "Comportement",
        "keep_segments": "Conserver les segments",
        "skip_existing": "Ignorer les fichiers existants",
        "verbose_logging": "Journalisation détaillée",
        "api_key": "Clé API:",
        "model": "Modèle:",
        "show": "Afficher",
        "hide": "Masquer",
        "start_transcription": "▶ Démarrer la Transcription",
        "stop": "⏹ Arrêter",
        "clear_log": "🗑 Effacer le Journal",
        "quit": "❌ Quitter",
        "language_selector": "Langue:",
        "error": "Erreur",
        "warning": "Avertissement",
        "success": "Succès",
        "error_no_input": "Veuillez sélectionner un fichier ou dossier audio.",
        "error_no_api_key": "Veuillez entrer une clé API.",
        "warning_already_processing": "La transcription est déjà en cours!",
    },
    # Portuguese (Partial)
    "pt": {
        "window_title": "Transcritor de Áudio",
        "tab_main": "📁 Configurações Principais",
        "tab_api": "🔌 Configuração da API",
        "tab_advanced": "⚙️ Avançado",
        "tab_transcription": "📝 Transcrição",
        "input": "Entrada",
        "audio_file_or_folder": "Arquivo ou Pasta de Áudio:",
        "choose_file": "Escolher Arquivo",
        "choose_folder": "Escolher Pasta",
        "output": "Saída",
        "browse": "Procurar",
        "api_key": "Chave API:",
        "model": "Modelo:",
        "show": "Mostrar",
        "start_transcription": "▶ Iniciar Transcrição",
        "stop": "⏹ Parar",
        "clear_log": "🗑 Limpar Registro",
        "quit": "❌ Sair",
        "language_selector": "Idioma:",
        "error": "Erro",
        "warning": "Aviso",
        "success": "Sucesso",
    },
    # Japanese (Partial)
    "ja": {
        "window_title": "オーディオ文字起こし",
        "tab_main": "📁 メイン設定",
        "tab_api": "🔌 API設定",
        "tab_advanced": "⚙️ 詳細設定",
        "tab_transcription": "📝 文字起こし",
        "input": "入力",
        "audio_file_or_folder": "オーディオファイルまたはフォルダ:",
        "choose_file": "ファイルを選択",
        "choose_folder": "フォルダを選択",
        "output": "出力",
        "browse": "参照",
        "api_key": "APIキー:",
        "model": "モデル:",
        "show": "表示",
        "start_transcription": "▶ 文字起こしを開始",
        "stop": "⏹ 停止",
        "clear_log": "🗑 ログをクリア",
        "quit": "❌ 終了",
        "language_selector": "言語:",
        "error": "エラー",
        "warning": "警告",
        "success": "成功",
    },
    # Chinese (Partial)
    "zh": {
        "window_title": "音频转录器",
        "tab_main": "📁 主要设置",
        "tab_api": "🔌 API配置",
        "tab_advanced": "⚙️ 高级",
        "tab_transcription": "📝 转录",
        "input": "输入",
        "audio_file_or_folder": "音频文件或文件夹:",
        "choose_file": "选择文件",
        "choose_folder": "选择文件夹",
        "output": "输出",
        "browse": "浏览",
        "api_key": "API密钥:",
        "model": "模型:",
        "show": "显示",
        "start_transcription": "▶ 开始转录",
        "stop": "⏹ 停止",
        "clear_log": "🗑 清除日志",
        "quit": "❌ 退出",
        "language_selector": "语言:",
        "error": "错误",
        "warning": "警告",
        "success": "成功",
    },
    # Italian (Partial)
    "it": {
        "window_title": "Trascrittore Audio",
        "tab_main": "📁 Impostazioni Principali",
        "tab_api": "🔌 Configurazione API",
        "tab_advanced": "⚙️ Avanzate",
        "tab_transcription": "📝 Trascrizione",
        "input": "Ingresso",
        "audio_file_or_folder": "File o Cartella Audio:",
        "choose_file": "Scegli File",
        "choose_folder": "Scegli Cartella",
        "output": "Uscita",
        "browse": "Sfoglia",
        "api_key": "Chiave API:",
        "model": "Modello:",
        "show": "Mostra",
        "start_transcription": "▶ Avvia Trascrizione",
        "stop": "⏹ Ferma",
        "clear_log": "🗑 Cancella Log",
        "quit": "❌ Esci",
        "language_selector": "Lingua:",
        "error": "Errore",
        "warning": "Avviso",
        "success": "Successo",
    },
    # Dutch (Partial)
    "nl": {
        "window_title": "Audio Transcriber",
        "tab_main": "📁 Hoofdinstellingen",
        "tab_api": "🔌 API Configuratie",
        "tab_advanced": "⚙️ Geavanceerd",
        "tab_transcription": "📝 Transcriptie",
        "input": "Invoer",
        "audio_file_or_folder": "Audiobestand of Map:",
        "choose_file": "Bestand Kiezen",
        "choose_folder": "Map Kiezen",
        "output": "Uitvoer",
        "browse": "Bladeren",
        "api_key": "API Sleutel:",
        "model": "Model:",
        "show": "Tonen",
        "start_transcription": "▶ Transcriptie Starten",
        "stop": "⏹ Stoppen",
        "clear_log": "🗑 Log Wissen",
        "quit": "❌ Afsluiten",
        "language_selector": "Taal:",
        "error": "Fout",
        "warning": "Waarschuwing",
        "success": "Succes",
    },
    # Russian (Partial)
    "ru": {
        "window_title": "Аудио Транскрибер",
        "tab_main": "📁 Основные Настройки",
        "tab_api": "🔌 Настройки API",
        "tab_advanced": "⚙️ Расширенные",
        "tab_transcription": "📝 Транскрипция",
        "input": "Ввод",
        "audio_file_or_folder": "Аудиофайл или Папка:",
        "choose_file": "Выбрать Файл",
        "choose_folder": "Выбрать Папку",
        "output": "Вывод",
        "browse": "Обзор",
        "api_key": "API Ключ:",
        "model": "Модель:",
        "show": "Показать",
        "start_transcription": "▶ Начать Транскрипцию",
        "stop": "⏹ Остановить",
        "clear_log": "🗑 Очистить Лог",
        "quit": "❌ Выход",
        "language_selector": "Язык:",
        "error": "Ошибка",
        "warning": "Предупреждение",
        "success": "Успех",
    },
    # Korean (Partial)
    "ko": {
        "window_title": "오디오 변환기",
        "tab_main": "📁 기본 설정",
        "tab_api": "🔌 API 구성",
        "tab_advanced": "⚙️ 고급",
        "tab_transcription": "📝 변환",
        "input": "입력",
        "audio_file_or_folder": "오디오 파일 또는 폴더:",
        "choose_file": "파일 선택",
        "choose_folder": "폴더 선택",
        "output": "출력",
        "browse": "찾아보기",
        "api_key": "API 키:",
        "model": "모델:",
        "show": "표시",
        "start_transcription": "▶ 변환 시작",
        "stop": "⏹ 중지",
        "clear_log": "🗑 로그 지우기",
        "quit": "❌ 종료",
        "language_selector": "언어:",
        "error": "오류",
        "warning": "경고",
        "success": "성공",
    },
    # Arabic (Partial)
    "ar": {
        "window_title": "محول الصوت",
        "tab_main": "📁 الإعدادات الرئيسية",
        "tab_api": "🔌 تكوين API",
        "tab_advanced": "⚙️ متقدم",
        "tab_transcription": "📝 النسخ",
        "input": "إدخال",
        "audio_file_or_folder": "ملف صوتي أو مجلد:",
        "choose_file": "اختر ملف",
        "choose_folder": "اختر مجلد",
        "output": "إخراج",
        "browse": "تصفح",
        "api_key": "مفتاح API:",
        "model": "النموذج:",
        "show": "عرض",
        "start_transcription": "▶ بدء النسخ",
        "stop": "⏹ إيقاف",
        "clear_log": "🗑 مسح السجل",
        "quit": "❌ خروج",
        "language_selector": "اللغة:",
        "error": "خطأ",
        "warning": "تحذير",
        "success": "نجاح",
    },
}


class I18n:
    """Internationalization handler for Audio Transcriber GUI."""

    def __init__(self, language: str = "en"):
        """
        Initialize i18n handler.

        Args:
            language: Initial language code (default: "en")
        """
        self.language = language if language in TRANSLATIONS else "en"
        self.fallback_language = "en"

    def set_language(self, language: str) -> None:
        """
        Set the current language.

        Args:
            language: Language code to set
        """
        if language in TRANSLATIONS:
            self.language = language
        else:
            self.language = self.fallback_language

    def get(self, key: str, **kwargs: Any) -> str:
        """
        Get translated string for key.

        Args:
            key: Translation key
            **kwargs: Format arguments for the translation string

        Returns:
            Translated and formatted string
        """
        # Try to get translation in current language
        translations = TRANSLATIONS.get(self.language, {})
        text = translations.get(key)

        # Fallback to English if not found
        if text is None:
            text = TRANSLATIONS[self.fallback_language].get(key, key)

        # Format with kwargs if provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return unformatted if formatting fails

        return text

    def __call__(self, key: str, **kwargs: Any) -> str:
        """
        Shortcut for get().

        Args:
            key: Translation key
            **kwargs: Format arguments

        Returns:
            Translated string
        """
        return self.get(key, **kwargs)
