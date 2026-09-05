[English](ReleaseNote.md) | [简体中文](ReleaseNote_zh.md) | [繁體中文](ReleaseNote_zh_TW.md) | [日本語](ReleaseNote_ja.md) | [한국어](ReleaseNote_ko.md) | [Deutsch](ReleaseNote_de.md) | [Français](ReleaseNote_fr.md) | [Русский](ReleaseNote_ru.md) | [Español](ReleaseNote_es.md)

# ATBClone 릴리즈 노트 (Release Notes)

이 문서는 **ATBClone**의 모든 주요 업데이트, 새로운 기능, 성능 개선 및 버그 수정 사항을 기록합니다.

---

## [v1.3.0] - 2026-09-05

### 🔬 Mach-O 헤드룸 탐색 및 안전 검증 (Headroom Probing)
- **정적 바이너리 헤더 공간 검사**:
  - Mach-O 바이너리를 수정하기 전에 로드 명령 구역(`sizeofcmds`)과 첫 번째 섹션 사이의 여유 패딩을 정밀 검사하는 `_check_macho_injection_headroom`을 추가했습니다.
  - 헤더 여유 공간이 부족한 앱에서 무리한 `LC_LOAD_DYLIB` 삽입으로 인한 바이너리 손상 및 충돌 위험을 원천 차단했습니다.

### 🎛️ 주입 전략 구성 옵션 (`auto` / `dylib` / `launcher`)
- **전방위 주입 전략 제어 및 우아한 폴백**:
  - Recipe 모델, CloneTask, CloneRecord, CLI(`--injection-strategy`) 및 GUI(복제 마법사, 레시피 편집기) 전반에 `injection_strategy` 설정을 도입했습니다.
  - **자동 모드 (`auto`)**: Cocoa 앱의 헤더 여유 공간을 탐색하여 안전할 경우 dylib을 주입하고, 공간이 부족하면 알림과 함께 네이티브 C Launcher로 자동 폴백합니다.
  - **dylib 모드 (`dylib`)**: dylib 주입을 강제하며 공간 부족 또는 비호환 바이너리인 경우 명확한 진단 정보와 함께 `CloneError`를 발생시킵니다.
  - **런처 모드 (`launcher`)**: 원본 바이너리를 일체 수정하지 않고 네이티브 Mach-O C Launcher 래퍼를 강제 적용합니다.
  - 복제 상세 패널(`CloneDetailWindow`) 및 CLI `inspect`에서 실제 실행된 주입 전략을 실시간 표시합니다.

### 📚 사용자 설명서 및 가이드 전면 개편
- **심층 원리 문서화**:
  - `docs/guide/`의 사용자 가이드(영문 및 중문)와 README에 주입 전략 선택, dylib 아키텍처 및 헤드룸 탐색 원리를 체계적으로 정리했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 확장**:
  - 총 479개의 단위, 엔진, 탐색 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.2.1] - 2026-09-05

### 🧩 @executable_path 기반 dylib 주입 디커플링 (Fix #6)
- **동적 라이브러리 가로채기 안정성 강화**:
  - `HardCloneEngine`의 동적 라이브러리 참조 경로를 `@rpath`에서 `@executable_path/../Frameworks/libatbclone_env.dylib`로 전면 업그레이드했습니다.
  - 대상 바이너리의 `LC_RPATH` 종속성을 완전히 제거하여 WeChat 4.x와 같이 비표준 또는 축소된 rpath를 가진 앱에서의 dyld 로드 충돌 및 심볼 해석 실패 문제를 해결했습니다.
  - `Contents/Frameworks/ld/` 하위 디렉터리가 존재하는 경우 심볼릭 링크 폴백을 자동 생성하도록 지원합니다.

### ⚙️ 빌드 중간 산출물 및 Info.plist 버전 자동 동기화
- **버전 불일치 방지**:
  - `scripts/manage_version.py`에 표준 `plistlib` 기반 `PlistVersionTarget`을 추가하여 `build/` 디렉터리의 `Info.plist`(`CFBundleShortVersionString` 및 `CFBundleVersion`)와 `welcome.html`을 자동으로 동기화합니다.
  - `scripts/manage_version.py --show`에 빌드 중간 산출물 상태 및 `[OUT OF SYNC]` 경고 표시를 도입했습니다.
  - `scripts/build_gui.sh`를 보강하여 독립 패키징 시에도 번들 내부 버전과 설치 관리자 리소스가 항상 일치하도록 구현했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 확장**:
  - 총 468개의 단위, 엔진, 버전 관리 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.2.0] - 2026-09-02

### 🔔 네이티브 dylib 주입을 통한 macOS 알림 센터 및 메뉴 막대 상태 아이콘 복구
- **알림 배너 및 트레이 상태 아이콘 지원 (Fix #5)**:
  - `HardCloneEngine`에서 네이티브 Mach-O 동적 라이브러리(`.dylib`) 인터포즈 주입 메커니즘을 활성화했습니다.
  - NSUserNotificationCenter 및 NSStatusItem API를 가로채어 브리지함으로써 하드 복제 앱의 알림 배너 누락 및 메뉴 막대 트레이 아이콘 미표시 문제를 해결했습니다.

### 🌓 다크 모드 동적 감지 및 UI 시각 디자인 개선
- **시스템 외관 실시간 추적 (Fix #4)**:
  - macOS 시스템 외관(라이트/다크) 전환을 실시간으로 감지하여 테마 토큰을 동적으로 적용합니다.
- **카드 그리드 레이아웃 및 텍스트 대비 향상**:
  - 메인 화면의 카드 그리드 간격을 최적화하고 기본 창 너비를 확장하여 시각적 여유를 확보했습니다.
  - 로그 및 릴리즈 노트 창의 다크 모드 텍스트 명도 대비를 대폭 개선하여 가독성을 강화했습니다 (WCAG 2.1 AA 준수).

### 📖 문서 및 스크린샷 업데이트
- **경로 표준화 및 리소스 갱신**:
  - 기본 복제본 설치 경로를 `~/ATBClone/Apps`로 안내 문서를 일괄 갱신했습니다.
  - 고해상도 GUI 스크린샷 및 버전 관리 도구 안내를 최신화했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 확장**:
  - 총 462개의 단위, 엔진, 테마 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.1.1] - 2026-08-30

### 🧹 이전 프레임워크 버전 자동 정리 및 디스크 절약
- **디스크 최적화 및 코드 서명 검증 안정성 확보**:
  - `HardCloneEngine`이 `Contents/Frameworks/*.framework/Versions/` 내부의 비활성 잔여 구버전(Google Chrome, Chromium, Electron 앱의 업데이트 잔해)을 자동으로 정리합니다.
  - 서명 검증 시 발생하는 `embedded framework contains modified or invalid version` 오류를 방지하고 복제본당 수백 MB의 디스크 공간을 절약합니다.

### 🛡️ Python plistlib 기반 심층 권한(Entitlements) 정제
- **안전한 임시 파일 추출 및 제한된 권한 필터링**:
  - 원자적 임시 경로(`${TMPDIR:-/tmp}/atb_ent_XXXXXX`)를 사용하여 Entitlements를 안전하게 추출합니다.
  - `PlistBuddy` 및 Python `plistlib`을 통합하여 애플 개발자, 앱 그룹, iCloud, 샌드박스 등의 제한된 권한 접두사(`com.apple.developer.` 등)를 철저히 정제합니다.
  - dylib, Mach-O 바이너리, 내장 Frameworks, Helper 프로세스 및 루트 번들에 걸친 다단계 재서명을 적용했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 확장**:
  - 총 455개의 단위, 엔진, 레시피 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.1.0] - 2026-08-29

### 🤖 AI 클라이언트 및 LLM 도구 생태계 심층 지원
- **Claude Desktop 및 Claude Code 다중 실행 지원**:
  - `CLAUDE_CONFIG_DIR`을 자동 주입하고 각 복제본 전용 `~/.claude` 및 `~/.claude.json` 환경을 격리 및 복제합니다.
  - 번들 내부의 `CFBundleName`을 안전하게 보존하여 Claude Helper 보조 프로세스가 호스트 앱을 정상 조회하도록 보장합니다.
- **Google Antigravity 및 Gemini 생태계 지원**:
  - `GEMINI_HOME` 및 `ANTIGRAVITY_HOME` 환경 변수를 주입하여 `~/.gemini` 디렉터리를 인스턴스별로 독립 격리합니다.
- **OpenAI ChatGPT 및 Codex CLI 지원**:
  - `CODEX_HOME` 환경 변수를 주입하고 `~/.codex` 설정을 복제하여 다중 계정 동시 실행을 지원합니다.

### 🔑 macOS 키체인(Keychains) 자동 심볼릭 링크
- **자격 증명 보호 및 크래시 방지**:
  - `HOME` 디렉터리 리디렉션 시 `Library/Keychains` 심볼릭 링크를 자동 구성하여 키체인 누락 오류 및 자격 증명 조회 실패를 방지합니다.

### 🛡️ AMFI 권한 정제 및 코드 서명 안전성 강화
- **macOS Sonoma / Sequoia 호환성 최적화**:
  - Ad-Hoc 재서명 시 제한된 팀 범위 권한(`com.apple.application-identifier`, `keychain-access-groups` 등)을 안전하게 정제합니다.
  - Apple Mobile File Integrity(AMFI)에 의한 Helper 프로세스의 `SIGKILL` 강제 종료를 원천 방지합니다.

### 🚀 ProcessSingleton 바이너리 패치 범용화
- **Electron / AI 앱 다중 실행 호환성 확장**:
  - Mach-O ProcessSingleton 패치를 범용화하고 AI 클라이언트 레시피에 `--user-data-dir`을 자동 적용했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 확장**:
  - 총 453개의 단위, 엔진, 레시피 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.0.2] - 2026-08-26

### 🛡️ 샌드박스 박리 최적화 및 하드 복제 안정성 강화
- **하드 복제 대상 샌드박스 박리(`strip_sandbox: true`) 기본 적용**:
  - 하드 복제 전략을 사용하는 레시피에서 샌드박스 박리 메커니즘을 적용하여 Mach-O 수정 후 발생할 수 있는 샌드박스 권한 충돌 및 교착 상태를 방지했습니다.
  - WeChat(위챗) 하드 복제 설정을 최적화하여 래퍼 스크립트에서 런타임 디렉토리 구조(`Caches`, `Containers`, `Preferences`) 생성을 안전하게 보장합니다.

### 📚 내장 레시피 정리 및 기술적 제한 사항 문서화
- **공식 레시피 정비**:
  - 기업위챗(WeCom)의 상위 CEF 독점 IPC 단일 실행 제약에 따라 실험적 내장 레시피를 정리하고 문제 해결 가이드에 호환성 안내를 추가했습니다.
  - 서드파티 앱 다중 실행 모범 사례 및 사용자 정의 Recipe 작성 가이드를 정비했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 통과**:
  - 총 443개의 단위, 레시피 엔진 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.0.1] - 2026-08-26

### 🎨 Apple Design HIG 준수 및 시각적 디자인 개선
- **macOS Human Interface Guidelines 표준 적용**:
  - 전체 화면 및 대화상자에 대해 Apple Design HIG 감사 및 디자인 리팩토링을 완료했습니다.
  - 불필요한 이모지 장식을 정리하고 명확한 SF Pro 타이포그래피 계층 구조를 적용했습니다.
  - 사이드바 탐색에 네이티브 Cocoa 선택 강조 표시를 도입했습니다.
  - WCAG 2.1 AA 가독성 기준을 충족하도록 라이트 및 다크 모드 색상 대비를 강화했습니다.
  - 빈 상태 화면, 카드 그림자, 창 드래그 영역 및 컴포넌트 여백을 표준화했습니다.

### 📜 로그 최신순(역순) 표시 및 다국어 레이아웃 최적화
- **실시간 진단 편의성 향상 (`LogsView`)**:
  - 로그 뷰를 시간 역순(최신 로그 상단 배치)으로 렌더링하도록 변경하여 실시간 모니터링 효율을 극대화했습니다.
  - "새로고침" 및 "찾아보기" 버튼의 고정 너비 제한을 해제하여 다국어 환경에서 텍스트가 잘리는 현상을 방지했습니다.

### 🛡️ 복제 엔진 안정성 및 확장 속성(xattr) 예외 처리 강화
- **번들 쓰기 권한 보장 및 오류 방지**:
  - Mach-O 바이너리 수정 및 재서명 전에 복제본 번들에 쓰기 권한(`chmod -R u+w`)을 자동으로 부여합니다.
  - 읽기 전용 파일 시스템이나 보호된 파일의 확장 속성(`xattr -cr`) 제거 시 발생하는 경미한 오류를 안전하게 처리하여 복제 실패를 방지했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 확장**:
  - 총 443개의 단위, 엔진 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v1.0.0] - 2026-08-24

### 🚀 ATBClone 1.0.0 정식 버전 릴리즈
- **프로덕션 레디 macOS 앱 복제 생태계**:
  - ATBClone이 버전 1.0.0에 도달하여 macOS(Apple Silicon 및 Intel)를 위한 완성도 높은 앱 다중 실행 및 데이터 격리 솔루션을 완성했습니다.
  - 디스크 공간 낭비 없는 소프트 복제(Soft Clone)와 완전한 데이터/권한 격리를 제공하는 하드 복제(Hard Clone) 듀얼 엔진을 완벽하게 지원합니다.

### 🧬 심층 CEF(Chromium Embedded Framework) 패치 및 WeCom 지원
- **하이브리드 앱 다중 실행 엔진 혁신**:
  - WeCom(기업위챗) 등 복합 CEF 기반 엔터프라이즈 앱을 위한 타겟 바이너리 패치를 구현했습니다.
  - Helper 서브프로세스의 `GpuDataManager` FATAL 크래시를 해결하고 보조 프로세스 번들 ID(`.helper.atbclone.X`)를 안전하게 직렬화 격리했습니다.
  - 심볼릭 링크 허용 목록 주입 및 내부 샌드박스 충돌 방지를 통해 장시간 안정적인 다중 실행을 보장합니다.

### 🛡️ 번들 내부 전체 바이너리 재귀 서명 및 싱글톤 락 패치
- **중첩 프레임워크 및 dylib 완벽 재서명**:
  - `HardCloneEngine`을 개선하여 앱 번들 내부의 모든 Helper, Frameworks, XPC 서비스 및 dylib을 재귀적으로 안전하게 재서명합니다.
  - JIT 및 Hardened Runtime 권한을 온전히 보존하며 임시 디렉토리를 통한 서명 검증 오염을 방지했습니다.
- **프레임워크 ProcessSingleton 바이너리 패치**:
  - `patch_framework_singleton` 레시피 필드를 도입하여 불안정한 동적 인터포징 대신 Mach-O 바이너리 수준에서 프로세스 단일 실행 잠금을 해제합니다.

### 📋 상세 정보 화면 인터랙션 및 클립보드 연동 강화
- **원클릭 진단 데이터 내보내기**:
  - Cocoa 다중 행 텍스트 뷰와 `NSPasteboard`를 결합하여 복제본 상세 정보의 텍스트 선택 및 Markdown 진단 리포트 원클릭 복사 기능을 제공합니다.

### 🧪 테스트 및 품질 보증
- **테스트 커버리지**:
  - 총 441개의 단위, 엔진, 레시피 및 GUI 통합 테스트를 100% 통과했습니다.

---

## [v0.9.9] - 2026-08-24

### 📋 복제본 상세 창 텍스트 선택 및 "전체 정보 복사" 지원
- **텍스트 인터랙션 및 내보내기 강화**:
  - `CloneDetailWindow`의 모든 텍스트 레이블에 Cocoa 네이티브 텍스트 선택 모드(`setSelectable_`)를 적용하여 경로, Bundle ID, 인수를 손쉽게 드래그하여 복사할 수 있습니다.
  - 하단에 "전체 정보 복사" 버튼을 추가하여 복제본의 전체 진단 요약을 Markdown 형식으로 클립보드에 원클릭 복사할 수 있습니다.

### 🎨 macOS 네이티브 UI 디자인 및 간격 최적화
- **테마 토큰 및 카드 레이아웃 다듬기**:
  - `Theme`의 라이트 및 다크 모드 색상 토큰(`BG_APP`, `BG_CARD`, `BG_HOVER`, `BORDER`, `TEXT_PRIMARY`, `TEXT_MUTED`, `ACCENT`)을 개선했습니다.
  - 카드 둥근 모서리, 여백 및 위젯 간격을 표준화하여 전체 뷰의 네이티브 마감 품질을 향상했습니다.

### 📖 포괄적인 다국어 사용자 설명서 제공 (`docs/guide/`)
- **상세 사용자 가이드 구축**:
  - 영어(`docs/guide/en/`) 및 중국어(`docs/guide/zh-cn/`) 사용자 매뉴얼을 전면 수록했습니다.
  - 제1장(기본 작업 및 수명 주기), 제2장(고급 커스텀 레시피), 제3장(아키텍처 및 내부 원리), 제4장(자주 묻는 질문, 닥터 진단 및 문제 해결)을 포함합니다.

### 🧪 테스트 확장
- **안정성 검증**:
  - 전체 단위 및 GUI 통합 테스트를 431개로 확대했습니다.

---

## [v0.9.8] - 2026-08-24

### 🔒 샌드박스 Entitlements 추출 및 하드 복제 엔진 안정성 강화
- **원본 앱 서명 권한(Entitlements) 보존**:
  - `HardCloneEngine`을 개선하여 `codesign -d --entitlements :-`를 통해 원본 Mach-O 바이너리로부터 고유 권한을 안전하게 추출하고 유지합니다.
  - 재서명 시 빈 권한이나 손상된 권한 파일로 인한 앱 비정상 종료를 방지하는 검증 로직을 추가했습니다.
- **기본 레시피 샌드박스 컨테이너 격리 보장**:
  - WeChat, QQ, WeWork, WPS Office, LINE, Skype, CapCut 등 하드 복제 레시피 전반에서 `strip_sandbox: false` 설정을 유지하도록 표준화했습니다.
  - 개별 복제본이 독립된 컨테이너 경로(`~/Library/Containers/<new_bundle_id>`)에서 안전하게 실행되어 데이터 간섭을 방지합니다.

### 📚 프로젝트 문서 및 스키마 동기화
- **기술 문서 최신화**:
  - 영어(`README.md`) 및 중국어(`README_zh.md`) 문서를 최신 `app_type`, `strip_sandbox` 사양 및 CLI/GUI 기능에 맞춰 동기화했습니다.

### 🧪 테스트 및 품질 보증
- **테스트 통과**:
  - 총 428개의 단위, 코어 엔진 및 GUI 통합 테스트를 모두 통과했습니다.

---

## [v0.9.7] - 2026-08-24

### 🔍 지능형 앱 아키텍처 감지 및 맞춤형 언어 인자 주입
- **런타임 프레임워크 자동 인식 (`app_type`)**:
  - Recipe 모델에 `app_type` 필드(`electron`, `chromium`, `qt`, `flutter`, `native_cocoa`, `java`, `unknown`)를 추가했습니다.
  - `AppProber.detect_app_type`을 통해 앱 내부 Frameworks, dylib, JVM 구조를 분석하여 아키텍처를 자동 판별합니다.
  - 내장된 34개 레시피의 `app_type` 및 `strip_sandbox` 설정을 표준화했습니다.
- **프레임워크 적응형 언어 인자 주입**:
  - 앱 프레임워크에 맞춰 최적화된 언어 실행 인자를 동적으로 주입합니다 (Chromium/Electron: `--lang=`, Native Cocoa: `-AppleLanguages`, Java: `-user.language`).

### 🧬 Mach-O 바이너리 인자 지능형 탐색 및 검증
- **미지원 앱 데이터 디렉토리 인자 자동 탐지**:
  - `BinaryArgumentProber`를 구현하여 Mach-O 실행 파일의 문자열을 스캔하고 지원되는 데이터 디렉토리 인자(`--user-data-dir`, `--profile-directory`, `--datadir` 등)를 자동 감지합니다.
- **실행 인자 안정성 검증**:
  - `LaunchArgumentValidator`를 도입하여 복제본 생성 시 충돌하거나 지원되지 않는 플래그를 사전에 필터링합니다.

### 📋 복제본 주입 파라미터 상세 분석 및 원클릭 복사
- **주입 파라미터 인스펙터 (`CloneInspector`)**:
  - `CloneInspector`를 구현하여 복제본에 주입된 환경 변수, 프록시 설정, 다국어 설정 및 실행 인자를 상세하게 파싱합니다.
  - `CloneDetailWindow`에 "주입된 파라미터" 카드를 추가하고 원클릭 복사 기능을 제공합니다.

### ⚙️ 레시피 편집기 고급 설정 지원
- **시각화 레시피 편집기 확장 (`RecipeEditWindow`)**:
  - 앱 프레임워크 유형 선택, 실행 인자 편집, 프록시 설정, 환경 변수 주입 및 심볼릭 링크 화이트리스트 설정을 지원합니다.

### 🧪 테스트 확장
- **안정성 강화**:
  - 전체 단위 및 GUI 통합 테스트를 428개로 확대했습니다.

---

## [v0.9.6] - 2026-08-24

### 🖱️ 네이티브 Cocoa 테이블 헤더 클릭 정렬 지원
- **목록 헤더 인터랙티브 정렬**:
  - `CloneListView` 및 `RecipeListView`에 Cocoa `NSTableViewHeaderView` 클릭 정렬 패치를 구현했습니다.
  - 헤더 클릭 시 오름차순/내림차순 전환, 정렬 방향 화살표 표시 및 툴바 정렬 메뉴와 양방향 동기화를 지원합니다.
  - 정렬 후에도 선택된 행의 포커스를 안전하게 유지합니다.

### 📦 다중 선택 및 일괄 관리 기능
- **복제본 일괄 관리 (`CloneListView`)**:
  - 다중 행 선택(`multiple_select=True`) 및 선택 상태에 따른 툴바 버튼 활성화/비활성화를 지원합니다.
  - 여러 복제본의 일괄 업데이트 및 일괄 삭제(데이터 삭제 확인 대화상자 포함)가 가능합니다.
- **레시피 일괄 삭제 및 보호 기능 (`RecipeListView`)**:
  - 커스텀 레시피 다중 선택 삭제 지원.
  - 상황별 맞춤 대화상자: 기본 제공 읽기 전용 레시피 보호 안내, 혼합 선택 시 안전 필터링 삭제, 커스텀 레시피 일괄 삭제 확인.
  - 일괄 작업 중 동시 조작을 방지하는 Busy 잠금 적용.

### 🛠️ Xcode Command Line Tools 진단 및 닥터 뷰 강화
- **개발 도구체인 준비도 진단**:
  - `DoctorService`에 Xcode Command Line Tools(`xcode-select -p`, `codesign`, `lipo`, `otool`, `install_name_tool`) 점검 항목을 추가하고 문제 해결 가이드를 제공합니다.

### ℹ️ macOS 표준 "About" 대화상자 메타데이터 개선
- **Cocoa About 창 정보 표시 정상화**:
  - `orderFrontStandardAboutPanelWithOptions:`를 호출하여 버전 및 저작권 정보를 정확하게 렌더링합니다.

### 🧪 테스트 확장
- **테스트 범위 확장**:
  - 전체 단위 및 GUI 통합 테스트를 369개로 확대했습니다.

---

## [v0.9.5] - 2026-08-23

### 📝 다중 행 자동 줄바꿈 `WrappingLabel` 컴포넌트 추가 및 텍스트 레이아웃 개선
- **자동 줄바꿈 텍스트 렌더링**:
  - macOS Cocoa 환경에서 긴 텍스트가 창을 가로로 늘리는 Toga Label의 한계를 해결하기 위해 `WrappingLabel` 컴포넌트를 구현했습니다.
  - `NSTextField` 및 `cellSizeForBounds_`를 기반으로 컨테이너 너비에 맞춰 높이를 동적으로 재계산하여 긴 경로나 인수로 인한 텍스트 잘림을 방지합니다.
- **분석 보고서 및 상세 화면 텍스트 포맷 개선**:
  - `ProbeView`(앱 분석 보고서, 호환성 평가, 샌드박스 상태), `CloneDetailWindow`(실행 인수, Bundle ID, 데이터 디렉토리), `WizardWindow`에 `WrappingLabel`을 적용했습니다.

### 🧪 테스트 격리성 및 상태 분리 강화
- **동적 설정 평가 및 테스트 신뢰성 향상**:
  - `StateManager` 및 `RecipeLoader`의 기본 경로 평가 방식을 개선하여 테스트가 로컬 사용자 상태나 커스텀 규칙 파일에 영향받지 않도록 완벽히 격리했습니다.
- **테스트 확장**:
  - 전체 단위 및 GUI 통합 테스트를 347개로 확대했습니다.

---

## [v0.9.4] - 2026-08-23

### 📁 기본 루트 데이터 디렉토리 이동 (`~/ATBClone`)
- **직관적인 사용자 데이터 및 스토리지 관리**:
  - 기본 루트 디렉토리를 숨김 폴더 `~/.atbclone`에서 사용자 접근이 편리한 `~/ATBClone`(`~/ATBClone/Data/`, `~/ATBClone/clones.yaml`)으로 변경했습니다.
  - Finder 및 터미널에서 복제본 데이터 확인 및 백업 관리가 훨씬 편리해졌습니다.

### 🏷️ 앱 표시 이름 명시적 적용 및 다국어 덮어쓰기 정리
- **일관된 복제본 이름 표시**:
  - `SoftCloneEngine` 및 `HardCloneEngine`을 강화하여 `LSHasLocalizedDisplayName`을 제거하고 번들 내 다국어 `InfoPlist.strings`를 정리합니다.
  - Finder, Dock, Spotlight, 활성 상태 보기에서 원본 앱의 번역명 대신 사용자가 지정한 복제본 이름이 정확히 표시됩니다.

### 🔄 LaunchServices 자동 등록 및 즉시 갱신
- **아이콘 및 메타데이터 실시간 반영**:
  - 복제본 생성/업데이트 완료 후 `lsregister -f`를 실행하여 시스템 재시작 없이도 macOS가 아이콘과 메타데이터를 즉시 갱신하도록 처리했습니다.

### 📦 문서 및 테스트 스위트 갱신
- **새로운 경로 반영**:
  - CLI 안내, GUI 설정, README 및 341개 자동화 테스트를 모두 새 경로에 맞춰 동기화했습니다.

---

## [v0.9.3] - 2026-08-21

### 🛡️ 앱 검사 강화 및 마법사 내 iOS 래퍼 앱 즉시 차단
- **마법사 사전 검증 및 안내 대화상자**:
  - `AppInspector.inspect_app` 로직을 개선하여 앱 선택 또는 드래그 앤 드롭 시 `UIDeviceFamily` / `LSRequiresIPhoneOS` 구조를 즉시 분석하고 `is_ios_wrapper` 플래그를 설정합니다.
  - GUI 생성 마법사(`WizardWindow`)에서 iOS 래퍼 앱이 선택되면 즉시 다국어 경고 대화상자를 띄우고 입력을 초기화하여 사전 안내를 명확히 제공합니다.

### 🍏 macOS 종료 프로세스 최적화 및 Cocoa 리소스 정리
- **앱 종료 시 크래시 (Crash on Exit) 방지**:
  - `TrayService.disable()` 및 `ATBCloneApp.exit_app()`에서 종료 전 Cocoa 상태 표시줄 메뉴 및 아이콘의 target/action을 안전하게 해제하도록 개선했습니다.
  - 표준 Cocoa 이벤트 루프 종료(`NSApp.terminate_` / `os._exit(0)`)를 적용하여 트레이 메뉴 "종료" 또는 `Cmd+Q` 입력 시 발생하던 비정상 종료 문제를 완전히 해결했습니다.

### 📦 테스트 확장
- **테스트 스위트 확장**:
  - 전체 자동화 테스트를 341개로 확대했습니다.

---

## [v0.9.2] - 2026-08-21

### 🍏 macOS Dock 아이콘 동적 숨김 및 트레이 연동 강화
- **Dock 아이콘 자동 표시/숨김 제어**:
  - Cocoa AppKit 실행 정책(`NSApplicationActivationPolicy`)을 기반으로 Dock 아이콘의 동적 표시/숨김을 지원합니다.
  - "트레이로 최소화" 활성화 시 창을 닫거나 최소화하면 앱이 보조 모드(`NSApplicationActivationPolicyAccessory`)로 전환되어 Dock 아이콘이 완전히 숨겨집니다.
  - 메뉴 막대 트레이에서 창을 복원할 때 일반 모드(`NSApplicationActivationPolicyRegular`)로 자동 복귀하여 Dock 아이콘이 다시 표시되고 창이 활성화됩니다.
- **Dock 클릭 시 창 복원 (Reopen Handler)**:
  - `AppDelegate`에 `applicationShouldHandleReopen:hasVisibleWindows:`를 연결하여 Dock 아이콘 클릭 시 메인 창이 자연스럽게 활성화되도록 개선했습니다.

### 📦 리소스 최적화 및 테스트 확장
- **아이콘 용량 최적화**:
  - `logo.icns` 및 `logo.png` 이미지 리소스를 압축 최적화하여 패키징 용량을 줄였습니다.
- **테스트 확장**:
  - 전체 자동화 테스트를 338개로 확대했습니다.

---

## [v0.9.1] - 2026-08-21

### 🛡️ iOS-on-Mac (Designed for iPad/iPhone) 앱 감지 및 안전한 차단
- **미지원 아키텍처 안전 차단**:
  - `AppProber` 및 복제 엔진(`SoftCloneEngine` / `HardCloneEngine`)을 개선하여 Apple Silicon용 iOS/iPadOS 래퍼 애플리케이션(`Wrapper/` 폴더 또는 `UIDeviceFamily` / `LSRequiresIPhoneOS=True` 포함 앱)을 정확히 감지합니다.
  - CLI (`atbclone clone`, `atbclone wizard`) 및 GUI 마법사에서 iOS 이식 앱 복제를 사전에 안전하게 차단하고 친절한 오류 메시지(`error_ios_wrapper_unsupported`)를 제공하여 번들 손상 및 실행 실패를 방지합니다.

### 🎨 패키징 스크립트 아이콘 자동 생성 지원
- **동적 `.icns` 생성 파이프라인**:
  - `scripts/build_gui.sh`에서 DMG 패키징 시 `sips` 및 `iconutil`을 활용하여 PNG 이미지를 다중 해상도 `.icns` 리소스로 자동 빌드하도록 개선했습니다.
  - 빌드 프로세스 전반의 리소스 검증을 강화했습니다.

### 🌐 다국어 로컬라이제이션
- **오류 안내 다국어 번역**:
  - iOS 래퍼 앱 차단 안내 메시지를 9개 언어 전체에 반영했습니다.
- **테스트 확장**:
  - 전체 단위 및 GUI 통합 테스트를 336개로 확대했습니다.

---

## [v0.9.0] - 2026-08-21

### 🌐 클론별 독립 언어 및 로케일 (Locale) 격리 지원
- **클론 전용 실행 언어 설정 (`--language` / `--locale`)**:
  - 각 클론 애플리케이션에 macOS 시스템 언어 및 원본 앱 설정과 독립된 전용 표시 언어와 로케일을 지정할 수 있습니다.
  - CLI (`atbclone clone`, `atbclone wizard`)에 `--language` / `--locale` 옵션을 추가하고 GUI 마법사 및 편집 창에 언어 선택 드롭다운을 제공합니다.
  - 소프트 클론 실행 스크립트 및 하드 클론 바이너리에 `AppleLanguages`와 `AppleLocale` 기본 설정 및 환경 변수를 자동 주입합니다.
  - BCP-47 언어 코드를 해석하는 `atbclone.core.locale` 모듈을 도입했습니다.

### 🆔 다중 클론 생성 시 Bundle ID 자동 채번 및 충돌 방지
- **고유한 번들 식별자 자동 생성**:
  - `AppInspector.find_next_bundle_id` 알고리즘을 도입하여 등록된 클론 상태와 파일 시스템을 스캔하고 충돌 없는 순차적 Bundle ID(`com.vendor.app.atb1`, `atb2` 등)를 생성합니다.

### 🍏 메뉴 막대 트레이 복원 및 창 수명 주기 개선
- **안정적인 트레이 창 활성화**:
  - 메뉴 막대 트레이(`TrayService`)에서 메인 창을 복원할 때 Cocoa 활성화, 최소화 해제 및 포커스 전환 로직을 강화했습니다.
  - "트레이로 최소화" 활성화 시 창 닫기 동작(`Cmd+W` 또는 빨간색 신호등 버튼)을 가로채어 앱을 종료하지 않고 트레이로 안전하게 숨깁니다.
  - 트레이 아이콘의 마우스 클릭(좌클릭, 우클릭, Ctrl+클릭) 이벤트를 안정화했습니다.

### ⚡ 클론 업데이트 경합 문제 해결 및 대상 경로 정리
- **안정적인 재생성 프로세스**:
  - `clone update` 수행 시 대상 경로를 사전에 완전히 정리하여 파일 경합 문제를 해결했습니다.
  - GUI 클론 카드 및 목록의 실시간 갱신을 최적화했습니다.

### 🎨 GUI 글꼴 크기 개선 및 문서 보강
- **시각적 완성도 향상**:
  - Cocoa 테이블 행 높이를 34px로 조정하고 드롭다운 텍스트 잘림 현상을 수정했습니다.
  - README에 GUI 사용 가이드 및 고화질 스크린샷을 추가했습니다.
- **테스트 확장**:
  - 전체 자동화 테스트를 329개로 확장했습니다.

---

## [v0.8.0] - 2026-08-20

### 🎨 macOS HIG 기반 시각 디자인 및 접근성 대폭 개선
- **Apple 네이티브 디자인 시스템 완전 준수**:
  - Apple Human Interface Guidelines (HIG)를 엄격히 준수하도록 GUI를 전면 개편했습니다. 표준 색상 팔레트, 시스템 폰트 계층(11pt~22pt), 넉넉한 여백 구조를 적용했습니다.
  - Cocoa 테이블 런타임 패치(`patch_cocoa`)를 통해 행 높이를 40px로 확대하고, 헤더 스타일 및 셀 폰트를 키워 가독성을 크게 개선했습니다.
  - 마법사, 환경 설정 및 편집 창의 입력 필드, 드롭다운, 스위치, 버튼 및 라벨 크기를 대폭 확대했습니다.
  - 테이블 하단 작업 버튼을 컴팩트한 macOS 네이티브 툴바 스타일로 정비했습니다.
  - 모든 관리 뷰의 기본 보기 방식을 **목록 보기 (List View)** 로 설정했습니다.

### 💾 통합 스토리지 설정 및 하위 디렉터리 자동 동기화
- **스토리지 관리 단순화**:
  - 환경 설정(`SettingsView`)의 스토리지 관리를 개편하여 루트 저장 디렉터리 변경 시 파생되는 모든 하위 경로(`clones.yaml`, `Data/`, `logs/`, `recipes/`)가 실시간으로 자동 동기화되도록 개선했습니다.
  - 디렉터리 유효성 및 상태 인디케이터를 추가했습니다.

### 🌐 HTTPS 프록시 프로토콜 지원
- **프록시 지원 확장**:
  - Recipe 모델, CLI (`atbclone clone`, `atbclone wizard`) 및 GUI 네트워크 설정에서 `https://` 프록시 URL 형식을 완벽하게 지원합니다.

### 📦 패키징 시스템 개선 및 테스트 확장
- **모듈 실행 진입점 및 DMG 빌드 강화**:
  - `src/atbclone/__main__.py` 진입점을 추가하여 `python -m atbclone` 직접 실행을 지원합니다.
  - `scripts/build_gui.sh` 스크립트에 App Bundle 무결성 검증, 아이콘 확인 및 서명 검사 기능을 추가했습니다.
- **테스트 확장**:
  - 전체 단위 및 GUI 통합 테스트를 304개로 확대했습니다.

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
