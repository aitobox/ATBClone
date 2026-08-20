[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 릴리즈 노트 (Release Notes)

이 문서는 **ATBClone**의 모든 주요 업데이트, 새로운 기능, 성능 개선 및 버그 수정 사항을 기록합니다.

---

## [v0.7.0] - 2026-08-20

### 🖥️ 네이티브 BeeWare Toga GUI 데스크톱 애플리케이션
- **모던한 Ice-Blue 그래픽 인터페이스**:
  - BeeWare Toga 기반의 macOS 네이티브 데스크톱 앱(`atbclone-gui`)을 출시했습니다.
  - 사이드바 내비게이션과 카드 그리드 레이아웃을 통해 클론 관리(`ClonesView`), 앱 심층 분석(`ProbeView`), 레시피 관리(`RecipesView`), 로그 뷰어(`LogsView`), 전체 설정(`SettingsView`)을 제공합니다.
  - `.app` 드래그 앤 드롭을 지원하는 직관적인 시각적 클론 생성 마법사를 지원합니다.

### 🍏 macOS 메뉴 막대 시스템 트레이 및 최소화 지원
- **시스템 트레이 서비스 (TrayService)**:
  - `NSStatusBar` 및 `NSStatusItem`을 통한 네이티브 메뉴 막대 트레이 아이콘과 퀵 메뉴(메인 창 열기, 클론 생성, 빠른 실행, 설정, 종료)를 통합했습니다.
  - "시스템 트레이로 최소화" 설정을 지원하여 Cocoa Selector 및 `NSWindowDelegate`를 통한 부드러운 창 숨김 및 복원을 제공합니다.

### 📖 GUI 다국어 릴리즈 노트 뷰어
- **내장 Release Notes 창**:
  - 환경 설정 화면에서 바로 열 수 있는 `ReleaseNotesWindow`를 구현했습니다.
  - 9개 언어 드롭다운을 통해 번역된 Markdown 릴리즈 노트를 실시간으로 확인할 수 있습니다.

### 📝 통합 작업 로그 시스템 (Unified Logger)
- **로그 파일 영속화 및 실시간 브로드캐스트**:
  - CLI와 GUI를 아우르는 `atbclone.core.logger`를 도입하여 파일 저장(`~/.atbclone/logs/atbclone.log`) 및 실시간 스트림(`LogBroadcastHandler`)을 지원합니다.
  - GUI 로그 뷰어에서 실시간 스트리밍, 레벨 필터링, 검색, 로그 내보내기 및 삭제를 지원합니다.

### 📦 레시피 추가 및 테스트 확장
- **인기 앱 레시피 지원**: **Claude Desktop** (`com.anthropic.claudefordesktop`), **Telegram** (`ru.keepcoder.Telegram`), **Cursor** 레시피를 추가 및 정비했습니다.
- **테스트 스위트 확장**: 전체 299개 단위 및 GUI 통합 테스트를 통해 안정성을 검증했습니다.

---

## [v0.6.0] - 2026-08-19

### 📂 사용자 지정 데이터 디렉터리 지원
- **클론 데이터 저장 경로 사용자 정의 (`--data-dir`)**:
  - `atbclone clone` 명령어에 `--data-dir` 옵션을 추가하여 외장 SSD나 특정 작업 디렉터리에 클론 데이터를 저장할 수 있도록 지원합니다.
  - 대화형 마법사(`atbclone wizard`)에 사용자 지정 데이터 디렉터리 설정 단계를 통합했습니다.
  - Recipe 모델 및 엔진에서 동적 데이터 디렉터리 변수 해석을 지원합니다.

### 🗑️ 클론 제거 및 데이터 정리 기능 강화 (`atbclone remove`)
- **안전한 데이터 정리 옵션 및 확인 절차**:
  - `atbclone remove`에 `--purge-data` 옵션을 추가하여 앱 본체와 사용자 데이터 디렉터리를 일괄 삭제할 수 있습니다.
  - `--keep-data` 옵션을 통해 앱만 제거하고 사용자 설정 데이터를 보존할 수 있습니다.
  - 대화형 제거 프롬프트에 데이터 보존 여부를 명확히 선택할 수 있는 확인 대화상자를 추가했습니다.
  - 잔여 데이터 디렉터리 및 권한 문제에 대한 안전 진단을 개선했습니다.

### 🆔 Bundle ID 생성 표준화 및 다국어 지원
- **표준화된 Bundle ID 생성**:
  - `AppInspector.generate_bundle_id`를 도입하여 `clone`, `wizard`, `update` 간 Bundle ID 형식을 일관되게 통일했습니다.
- **다국어 로컬라이제이션 확장**:
  - 데이터 디렉터리 입력, 제거 확인 및 정리 상태 메시지를 9개 언어 전체에 반영했습니다.
- **테스트 확장**:
  - 전체 단위 테스트를 213개로 확장하여 사용자 지정 경로 및 제거 프로세스를 철저히 검증합니다.

---

## [v0.5.0] - 2026-08-19

### 🔐 Apple 코드 서명 및 공증(Notarization) 지원
- **Hardened Runtime 및 공식 코드 서명**:
  - Apple Developer ID Application 인증서 서명, Hardened Runtime(`--options runtime`), 타임스탬프 및 맞춤형 JIT 실행 권한(`scripts/entitlements.plist`)을 기본 지원합니다.
  - 키체인 프로필(`--keychain-profile`)을 통해 Apple 공증을 자동으로 수행하는 `scripts/notarize.sh` 스크립트를 추가했습니다.
  - `scripts/build_cli.sh` 및 `scripts/release.sh`에서 `--sign-identity`, `--skip-sign`, `--notarize` 옵션을 지원하며, 인증서가 없을 경우 ad-hoc 서명으로 자동 전환됩니다.

### 🚀 Chromium 브라우저 하드 복제 및 실행 인수 주입
- **`HardCloneEngine` 실행 인수(`launch_args`) 주입**:
  - 환경 변수 격리 외에도 바이너리 래퍼에 `--user-data-dir={{ATB_DATA_DIR}}`와 같은 실행 인수를 주입할 수 있도록 `HardCloneEngine`을 개선했습니다.
  - **Google Chrome**, **Microsoft Edge**, **Arc Browser**의 기본 레시피를 `hard_clone` 전략으로 업그레이드하여 완전한 App Bundle 복제 및 독립된 Dock/Finder 식별을 제공합니다.
- **CLI 전략 재정의 지원**:
  - `atbclone clone` 명령어에 `--strategy` 옵션(`hard_clone` 또는 `soft_clone`)을 추가하여 기본 레시피 전략을 재정의할 수 있습니다.

### ⚡ 프로세스 포워딩 및 테스트 확장
- **프로세스 제어 최적화**: `SoftCloneEngine` 래퍼 스크립트에서 표준 `exec "$@"` 프로세스 전달 방식을 적용했습니다.
- **테스트 스위트 확장**: 전체 199개 단위 테스트를 통해 코드 서명, 공증 스크립트 및 복제 전략을 철저히 검증합니다.

---

## [v0.4.0] - 2026-08-19

### 🌐 9개 언어 완전 지원 CLI 및 문서 체계
- **CLI 전체 명령어 9개 언어 다국어화 지원**:
  - `atbclone.core.i18n` 엔진을 확장하여 영어, 중국어 간체, 중국어 번체, 일본어, 한국어, 독일어, 프랑스어, 러시아어, 스페인어 총 9개 언어를 지원합니다.
  - 모든 CLI 명령어(`wizard`, `clone`, `probe`, `list`, `recipe`, `doctor`, `update`, `remove`, `version`)에 다국어 프롬프트, 테이블 및 오류 진단이 적용되었습니다.
- **다국어 Release Notes 표준화**:
  - `docs/release/` 디렉터리 내 9개 언어 릴리즈 노트를 체계화하고 언어 탐색 링크를 정비했습니다.

### 🔄 자동화된 릴리즈 및 버전 동기화 파이프라인
- **9개 언어 ReleaseNotes 자동 검증 메커니즘**:
  - `scripts/manage_version.py` 및 `scripts/release.sh`를 개선하여 태그 생성 전 9개 언어 릴리즈 노트의 버전 기재 여부를 자동 검증합니다.
  - 릴리즈 문서 누락을 방지하는 `--check-notes` 옵션이 추가되었습니다.
- **테스트 스위트 확장**:
  - 자동화 테스트 케이스가 총 191개로 확장되어 다국어 렌더링 및 릴리즈 프로세스를 철저히 검증합니다.

---

## [v0.3.0] - 2026-08-19

### 🌐 국제화 및 다국어 지원 (i18n)
- **macOS 시스템 언어 자동 감지**:
  - `AppleLanguages` 및 `AppleLocale`을 통해 macOS 시스템 선호 언어를 자동으로 감지하는 `atbclone.core.i18n` 엔진을 도입했습니다.
  - CLI 대화형 마법사, 터미널 프롬프트, 테이블 헤더 및 에러 로그가 한국어/영어/중국어 환경에 맞춰 스마트하게 전환됩니다.
  - 환경 변수 `ATBCLONE_LANG`(`ATBCLONE_LANG=en` 또는 `ATBCLONE_LANG=zh`)을 통해 실행 언어를 수동으로 재정의할 수 있습니다.
- **다국어 문서 지원**:
  - `Readme.md`를 기본 영문 문서로 표준화하고, 중국어 전체 문서를 `Readme_zh.md`로 제공합니다.
  - 9개 언어로 작성된 릴리즈 노트를 제공합니다: 영어, 중국어 간체, 중국어 번체, 일본어, 한국어, 독일어, 프랑스어, 러시아어, 스페인어.

### 🛠️ CLI 및 빌드 패키징 개선
- **대화형 마법사 i18n 통합**: `atbclone wizard`의 입력 프롬프트, 사용자 정의 표시 이름, `.icns` 아이콘 선택 및 프록시 설정이 다국어로 완벽 지원됩니다.
- **단독 바이너리 빌드 업그레이드**: Nuitka를 사용하여 다국어 리소스를 내장한 `./dist/ATBCloneCli` 단일 실행 바이너리를 재빌드하고 샌드박스 빌드 호환성(`PYTHONNOUSERSITE=1`)을 강화했습니다.
- **단위 테스트 스위트 강화**: `test_i18n.py`를 추가하고 모든 186개 자동화 테스트가 정상 통과함을 검증했습니다.

---

## [v0.2.0] - 2026-08-18

### 🚀 주요 신규 기능
- **대화형 클론 마법사 (`atbclone wizard`)**:
  - 터미널에서 `.app` 경로 드래그 앤 드롭 입력을 지원하는 단계별 마법사.
  - 클론 이름 자동 증가 감지 (예: `WeChat2`, `WeChat3`).
  - 사용자 정의 앱 표시 이름 및 `.icns` 아이콘 설정 지원.
  - 대화형 네트워크 프록시(HTTP / SOCKS5) 설정 및 계정 인증 지원.
- **지능형 딥 앱 프로버 (`atbclone probe`)**:
  - 모든 macOS 앱의 Mach-O 아키텍처(arm64, x86_64, Universal), 프레임워크(Electron, Flutter, Chromium, Qt, Cocoa) 및 샌드박스 권한(`com.apple.security.app-sandbox`)을 자동 분석.
  - 사전 등록되지 않은 앱에 대해서도 최적의 클론 전략(`hard_clone` / `soft_clone`)을 동적으로 추천하고 레시피 YAML을 자동 생성.
  - `atbclone clone` 실행 시 레시피가 없는 앱에 대해 프로버 엔진이 자동 실행되도록 통합.
- **단일 실행 바이너리 패키징**:
  - Nuitka를 기반으로 외부 종속성이 없는 네이티브 macOS arm64 단일 파일 실행 파일(`dist/ATBCloneCli`)을 컴파일하는 `scripts/build_cli.sh` 추가.

### ⚡ 개선 및 버그 수정
- `/Applications` 디렉토리 출력 시 권한 상승을 macOS 네이티브 `osascript` 대화 상자로 통합하여 1회 비밀번호 입력으로 처리.
- 공백이나 특수 문자가 포함된 경로를 보호하기 위해 전체 경로 처리에 `shlex.quote` 이스케이프 적용.

---

## [v0.1.0] - 2026-08-17

### 🌟 최초 릴리즈
- **듀얼 엔진 클로닝 아키텍처**:
  - **하드 클론 (Hard Clone)**: 앱 번들 전체 복제, `Info.plist` 수정, 바이너리 런처 스크립트 하이재킹을 통한 독립 `HOME` / `TMPDIR` 주입, 샌드박스 해제 및 ad-hoc 재서명.
  - **소프트 클론 (Soft Clone)**: Chromium 기반 브라우저 및 코드 에디터용 가벼운 런처 래퍼 생성 및 `--user-data-dir` 주입.
- **18개 이상의 인기 앱 기본 레시피 지원**:
  - 메신저: WeChat, QQ, Telegram, LINE, Slack, Discord, Skype.
  - AI 클라이언트: ChatGPT (Codex), Gemini, Antigravity, Antigravity IDE.
  - 브라우저 및 도구: Google Chrome, Microsoft Edge, Firefox, Arc, Cursor, VS Code, Zed.
- **완벽한 CLI 명령어 지원**:
  - `clone`: 앱 클론 생성.
  - `list`: 생성된 클론 목록 및 상태 조회.
  - `update`: 원본 앱 업데이트 후 사용자 데이터를 유지한 상태로 클론 동기화.
  - `remove`: 클론 안전 삭제 (데이터 정리 옵션 지원).
  - `recipe`: 내장 레시피 목록 및 로컬 오버라이드 확인.
  - `doctor`: 환경 도구 체인(`codesign`, `xcode-select`, `PlistBuddy`) 자동 검사.
