import os

KO_DIR = "docs/guide/ko"

# 02-advanced-custom-recipes.md
ch02 = """# 제2장: 사용자 정의 레시피 및 기본 매개변수

ATBClone 은 수많은 주요 앱을 위한 기본 레시피를 내장하고 있지만, 사내 업무 도구, 비주류 전문 소프트웨어, 최신 앱 등을 복제해야 하는 경우도 있습니다. 본 장에서는 **App Prober (스마트 프로버)** 를 통한 자동 분석과 시각적 레시피 편집기를 활용한 사용자 정의 규칙 생성 절차를 설명합니다.

---

## 📑 목차

- [App Prober 를 통한 미지원 앱 정밀 진단](#app-prober-)
  - [GUI 원클릭 분석](#gui-)
  - [CLI 터미널 상세 분석](#cli-)
  - [진단 결과 판정 기준](#_1)
- [시각적 레시피 편집기 사용법](#_2)
- [레시피 YAML 구조 및 기본 매개변수 해설](#yaml-)
  - [1. bundle_id (번들 식별자)](#1-bundle_id-)
  - [2. strategy (격리 전략)](#2-strategy-)
  - [3. strip_sandbox (샌드박스 박리)](#3-strip_sandbox-)
  - [4. proxy (네트워크 프록시)](#4-proxy-)
- [사용자 정의 레시피 테스트 및 저장](#_3)

---

## 🔍 App Prober 를 통한 미지원 앱 정밀 진단

ATBClone 에 내장된 **App Prober** 정적/동적 분석 도구는 앱 내부 바이너리, 코드 서명 메타데이터, 샌드박스 권한 목록(Entitlements)을 수초 내에 포괄적으로 스캔합니다.

### GUI 원클릭 분석
1. 사이드바 또는 도구 메뉴에서 **"레시피 관리"** 를 선택합니다.
2. 우측 상단의 **"앱 진단 (Probe App)"** 버튼을 클릭합니다.
3. 분석할 `.app` 번들을 선택하면 즉시 상세 정보가 표시됩니다:
   * **프레임워크 유형**: Electron, Chromium, Flutter, Qt, 네이티브 Cocoa/AppKit, Java 등.
   * **샌드박스 상태**: App Sandbox 활성화 여부.
   * **권장 전략**: `Hard Clone` 또는 `Soft Clone`.

### CLI 터미널 상세 분석
터미널에서 직접 진단을 수행할 수도 있습니다:

```bash
atbclone probe /Applications/Slack.app
```

출력 예시:

```text
================================================================================
ATBClone Application Prober
Target: /Applications/Slack.app
================================================================================
[+] Bundle ID: com.tinyspeck.slackmacgap
[+] Executable: /Applications/Slack.app/Contents/MacOS/Slack
[+] Framework: Electron (Chromium-based)
[+] App Sandbox: Enabled (com.apple.security.app-sandbox)
[+] Hardened Runtime: Yes
[+] Recommendation: Strategy=hard_clone, StripSandbox=true
================================================================================
```

### 진단 결과 판정 기준
* **Electron / Chromium 계열 앱**: 일반적으로 `soft_clone` 으로 충분하지만, 알림 센터 독립성이나 메뉴바 상주를 완전히 분리하려면 `hard_clone` 과 `strip_sandbox: true` 조합이 가장 안정적입니다.
* **네이티브 Cocoa / 샌드박스 적용 앱**: 원본 앱이 샌드박스 내에서 실행되는 경우, `hard_clone` 과 `strip_sandbox: true` 가 필수적입니다.

---

## 🛠️ 시각적 레시피 편집기 사용법

진단 완료 후 **"레시피 생성 및 편집"** 을 클릭하면 양식 기반 편집기가 열립니다:

```text
+-------------------------------------------------------------+
|  📝 레시피 편집기 - Slack.yaml                                |
|                                                             |
|  앱 이름:       [ Slack                                  ]  |
|  Bundle ID:     [ com.tinyspeck.slackmacgap              ]  |
|  격리 전략:     (●) Hard Clone (하드)   ( ) Soft Clone     |
|  샌드박스 해제: [✔] 샌드박스 제한 강제 제거 (권장)           |
|  프록시 구성:   [ http://127.0.0.1:7890                  ]  |
|                                                             |
|  [ YAML 미리보기 ]       [ 테스트 실행 ]       [ 레시피 저장 ]|
+-------------------------------------------------------------+
```

---

## 📜 레시피 YAML 구조 및 기본 매개변수 해설

생성된 레시피 파일은 간결한 YAML 형식으로 저장됩니다:

```yaml
version: "1.0"
name: "Slack"
description: "Slack 메신저용 다중 인스턴스 격리 설정"

# 기본 매개변수
bundle_id: "com.tinyspeck.slackmacgap"
strategy: "hard_clone"
strip_sandbox: true

# 네트워크 프록시 (선택 사항)
proxy:
  type: "http"
  host: "127.0.0.1"
  port: 7890
```

### 1. bundle_id (번들 식별자)
대상 앱의 공식 Bundle Identifier 를 지정합니다 (예: `com.tencent.xinWeChat`). 이 값은 클론 생성 시 새로운 고유 ID 로 자동 치환됩니다.

### 2. strategy (격리 전략)
* `hard_clone`: 바이너리 전체를 복사하고 환경 변수 래퍼를 주입합니다.
* `soft_clone`: 바이너리를 복제하지 않고 데이터 디렉토리 인자만 전달하여 실행합니다.

### 3. strip_sandbox (샌드박스 박리)
`true` 로 설정하면 Mach-O 바이너리 및 서명에서 `com.apple.security.app-sandbox` 플래그를 완전히 제거합니다. 이를 통해 클론 앱이 원본의 제한된 컨테이너(`~/Library/Containers/`)에 종속되지 않고 임의의 사용자 지정 데이터 폴더를 자유롭게 접근할 수 있습니다.

### 4. proxy (네트워크 프록시)
클론 앱의 네트워크 트래픽을 지정된 프록시 서버로 라우팅합니다.
* `type`: `http`, `https`, 또는 `socks5`.
* `host`: IP 주소 또는 도메인.
* `port`: 포트 번호.

---

## 💾 사용자 정의 레시피 테스트 및 저장

1. 하단의 **"테스트 실행 (Dry Run)"** 을 클릭하여 오류가 없는지 사전 점검합니다.
2. 문제가 없으면 **"레시피 저장"** 을 클릭합니다. 저장된 레시피는 이후 마법사의 추천 목록에 자동으로 노출됩니다.
"""

# 03-under-the-hood-and-internals.md
ch03 = """# 제3장: 내부 동작 원리 및 고급 매개변수 심층 분석

본 장에서는 ATBClone 의 심층 아키텍처, 소프트 클론과 하드 클론의 저수준 구현 원리, 바이너리 래퍼 하이재킹 기술, 고급 YAML 매개변수 및 동적 경로 매크로를 상세히 분석합니다.

---

## 📑 목차

- [격리 아키텍처 메커니즘 비교](#_1)
  - [소프트 클론 (Soft Clone) 내부 구조](#soft-clone)
  - [하드 클론 (Hard Clone) 내부 구조](#hard-clone)
- [하드 클론 3대 핵심 기술 분석](#3)
  - [1. 번들 식별자 (Bundle ID) 변조](#1-bundle-id)
  - [2. 바이너리 래퍼 하이재킹 (Wrapper Hijack)](#2-wrapper-hijack)
  - [3. 샌드박스 박리 및 애드혹 재서명](#3-)
- [데이터-로직 완전 분리 아키텍처](#-)
- [고급 레시피 매개변수 해설](#_2)
  - [1. environment_injection (환경 변수 주입)](#1-environment_injection)
  - [2. symlink_whitelist (심볼릭 링크 화이트리스트)](#2-symlink_whitelist)
  - [3. launch_arguments (실행 인수)](#3-launch_arguments)
  - [4. plist_overrides (Info.plist 재정의)](#4-plist_overrides-infoplist-)
  - [5. 동적 경로 매크로 변수](#5)
- [고급 사용자 정의 레시피 전체 YAML 예시](#yaml)

---

## 🏗️ 격리 아키텍처 메커니즘 비교

### 소프트 클론 (Soft Clone) 내부 구조
소프트 클론은 Chromium, Electron 또는 커맨드라인 인수를 통한 데이터 디렉토리 변경을 공식 지원하는 앱에 적합합니다. 수백 메가바이트의 바이너리를 복제하지 않고 수 킬로바이트 수준의 경량 런처 스크립트만 생성합니다.

```text
[Soft Clone 런처]
       │ 실행 인수 전달
       ▼
/Applications/Cursor.app/Contents/MacOS/Cursor --user-data-dir="~/ATBClone/Data/Cursor-Work"
```

* **장점**: 디스크 사용량 제로에 수렴, 생성 및 업데이트가 1초 내에 완료.
* **제약**: Dock 아이콘이 원본 앱과 묶일 수 있으며, TCC 권한이 원본과 공유됩니다.

---

### 하드 클론 (Hard Clone) 내부 구조
하드 클론은 WeChat, 카카오톡, Telegram, Discord, Slack 등 완벽한 시스템 독립성과 데이터 격리가 필요한 모든 네이티브 앱에 적용됩니다.

```mermaid
graph TD
    A[원본 앱 /Applications/WeChat.app] -->|App 번들 완전 복제| B[클론 앱 ~/ATBClone/Apps/WeChat-2.app]
    B --> C[1. CFBundleIdentifier 고유값 변경]
    B --> D[2. 원본 실행 파일을 .real 로 변경]
    B --> E[3. 래퍼 셸 스크립트를 실행 파일 위치에 배치]
    B --> F[4. 샌드박스 권한 박리 및 애드혹 재서명]
    
    E -->|실행 시 환경 변수 교체| G["HOME=~/ATBClone/Data/WeChat-2"]
    G --> H[WeChat.real 실행]
```

---

## ⚡ 하드 클론 3대 핵심 기술 분석

### 1. 번들 식별자 (Bundle ID) 변조
`Info.plist` 의 `CFBundleIdentifier`(예: `com.tencent.xinWeChat`)를 고유 식별자(`com.tencent.xinWeChat.atbclone.work`)로 수정합니다. macOS 는 이를 완전히 새로운 앱으로 인식하여 알림, TCC 보안 권한, 윈도우 관리를 독립 처리합니다.

### 2. 바이너리 래퍼 하이재킹 (Wrapper Hijack)
하드 클론의 핵심 기술입니다:
1. `Contents/MacOS/<Executable>` 바이너리를 `<Executable>.real` 로 이름을 바꿉니다.
2. 동일한 이름의 POSIX 셸 스크립트를 생성하고 실행 권한(`chmod +x`)을 부여합니다.
3. 래퍼 스크립트에서 다음 환경 변수를 가로채 재정의한 후 백그라운드의 `.real` 바이너리를 호출합니다:
   * `export HOME="<격리된 데이터 경로>"`
   * `export TMPDIR="<격리된 데이터 경로>/tmp"`
   * `export XDG_DATA_HOME="<격리된 데이터 경로>/Library/Application Support"`
   * `export XDG_CONFIG_HOME="<격리된 데이터 경로>/Library/Preferences"`

이 방식을 통해 원본 코드를 단 한 줄도 수정하지 않고도 모든 파일 I/O 와 로컬 저장소를 지정된 독립 폴더로 유도합니다.

### 3. 샌드박스 박리 및 애드혹 재서명
App Sandbox 가 활성화된 앱은 시스템에 의해 `~/Library/Containers/<BundleID>` 경로로 접근이 엄격히 제한됩니다. ATBClone 은 바이너리에서 샌드박스 권한 플래그를 제거하고 macOS 표준 `codesign -f -s -` 로 재서명하여 임의의 사용자 지정 데이터 폴더에 자유롭게 접근할 수 있도록 권한을 개방합니다.

---

## 💎 데이터-로직 완전 분리 아키텍처

ATBClone 은 **"프로그램 로직(Apps)"** 과 **"사용자 데이터(Data)"** 를 완전히 분리하여 관리합니다:

* **로직 계층 (`~/ATBClone/Apps/`)**: 언제든지 안전하게 재생성, 삭제, 덮어쓰기 가능.
* **데이터 계층 (`~/ATBClone/Data/`)**: 대화 내용, 로컬 캐시, 설정이 안전하게 영구 보존.

원본 앱이 업데이트되어도 앱 본체만 최신 파일로 교체되고 데이터 디렉토리는 그대로 유지되므로 무손실 업데이트가 보장됩니다.

---

## ⚙️ 고급 레시피 매개변수 해설

### 1. environment_injection (환경 변수 주입)
클론 앱 실행 시 추가로 주입할 환경 변수를 지정합니다:

```yaml
environment_injection:
  ELECTRON_ENABLE_LOGGING: "1"
  NODE_ENV: "production"
  SSL_CERT_FILE: "{DATA_DIR}/certs/ca.pem"
```

### 2. symlink_whitelist (심볼릭 링크 화이트리스트)
격리 환경 내에서도 폰트, 색상 프로필 등 특정 시스템 리소스만 원본과 공유하려는 경우:

```yaml
symlink_whitelist:
  - "~/Library/Fonts"
  - "~/Library/ColorSync"
```

### 3. launch_arguments (실행 인수)
실행 시 자동으로 추가될 커맨드라인 플래그:

```yaml
launch_arguments:
  - "--disable-gpu-shader-disk-cache"
  - "--no-first-run"
```

### 4. plist_overrides (Info.plist 재정의)
`Info.plist` 의 특정 키를 사용자 정의 값으로 덮어씁니다:

```yaml
plist_overrides:
  NSHighResolutionCapable: true
  LSUIElement: false
```

### 5. 동적 경로 매크로 변수
* `{DATA_DIR}`: 대상 클론의 전용 데이터 디렉토리 경로.
* `{CLONE_NAME}`: 클론 앱의 이름.
* `{BUNDLE_ID}`: 생성된 새 Bundle Identifier.
* `{HOST_APP}`: 원본 앱의 전체 경로.

---

## 📋 고급 사용자 정의 레시피 전체 YAML 예시

```yaml
version: "1.0"
name: "Discord"
description: "Discord 용 프록시 및 환경 변수 주입 하드 클론 설정"

bundle_id: "com.hnc.discord"
strategy: "hard_clone"
strip_sandbox: true

injection_mode: "wrapper_hijack"

# 네트워크 프록시
proxy:
  type: "socks5"
  host: "127.0.0.1"
  port: 10808

# 환경 변수 주입
environment_injection:
  DISCORD_USER_DATA_DIR: "{DATA_DIR}/discord_data"

# 실행 인수
launch_arguments:
  - "--start-minimized"

# 심볼릭 링크 화이트리스트
symlink_whitelist:
  - "~/Library/Audio"
```
"""

# 04-faq-and-troubleshooting.md
ch04 = """# 제4장: 자주 묻는 질문 (FAQ), 시스템 진단 및 피드백

본 장에서는 사용자들이 자주 묻는 질문, 보안 및 계정 보호 주의사항, 내장 진단 도구인 Doctor 활용법, 오류 발생 시 GitHub Issue 제출 절차를 설명합니다.

---

## 📑 목차

- [자주 묻는 질문 (FAQ)](#faq)
  - [1. 클론을 생성하면 원본 앱의 데이터에 영향이 있나요?](#1)
  - [2. 클론 데이터는 어디에 저장되나요? 백업 및 이전 방법은?](#2)
  - [3. 계정이 차단(BAN)될 위험이 있나요?](#3-ban)
  - [4. 관리자 비밀번호 (Root / Sudo) 가 필요한가요?](#4-root-sudo)
  - [5. "확인되지 않은 개발자" 또는 손상 경고가 발생할 때 해결 방법은?](#5)
  - [6. 클론 앱의 아이콘을 변경하려면 어떻게 하나요?](#6)
  - [7. 메신저 앱에서 메뉴바 아이콘이나 알림이 작동하지 않을 때 해결 방법은?](#7)
- [시스템 환경 진단 (Doctor 도구)](#doctor-)
- [문제 발견 및 GitHub Issue 보고 절차 (표준 트러블슈팅)](#-github-issue-)
  - [1단계: 메인 화면에서 오류 클론 선택 후 "세부 정보" 클릭](#1-)
  - [2단계: "클론 세부 정보" 에서 진단 리포트 복사](#2-)
  - [3단계: GitHub Issue 에 제출](#3-github-issue-)
- [커뮤니티 및 지원](#_1)

---

## ❓ 자주 묻는 질문 (FAQ)

### 1. 클론을 생성하면 원본 앱의 데이터에 영향이 있나요?
**전혀 영향을 주지 않습니다.**
ATBClone 은 완전히 독립된 데이터 디렉토리(`~/ATBClone/Data/<클론이름>`)를 생성하여 사용합니다. 원본 앱의 데이터 및 캐시 디렉토리에는 일절 접근하지 않습니다.

### 2. 클론 데이터는 어디에 저장되나요? 백업 및 이전 방법은?
* **저장 위치**: 기본적으로 `~/ATBClone/Data/<클론이름>` 에 모든 데이터가 저장됩니다.
* **백업 및 이전**: 대시보드에서 클론 카드의 **"폴더 열기"** 아이콘을 클릭한 후 표시된 폴더를 외장 SSD 나 새 Mac 으로 복사하기만 하면 완벽하게 이전됩니다.

### 3. 계정이 차단(BAN)될 위험이 있나요?
ATBClone 은 **비침투형(Non-Invasive) 샌드박스 격리 기술**을 사용합니다. 통신 패킷을 변조하거나 메모리를 조작하는 불법 프로그램이 아닙니다. macOS 네이티브 환경 변수 리다이렉션을 통해 동작하므로 공식 앱이 실행되는 것과 기술적으로 동일하며 안전합니다.

또한 **독립 프록시 기능**을 함께 사용하면 앱별로 IP 주소를 분산시킬 수 있어 동일 IP 다중 접속 감지 위험을 방지할 수 있습니다.

### 4. 관리자 비밀번호 (Root / Sudo) 가 필요한가요?
**전혀 필요하지 않습니다.**
ATBClone 의 모든 파일 복제, 래퍼 생성, 애드혹 서명, 데이터 관리는 현재 사용자 권한(User Space) 내에서 완결됩니다. 시스템 시스템 파일(`/System`)을 수정하지 않습니다.

### 5. "확인되지 않은 개발자" 또는 손상 경고가 발생할 때 해결 방법은?
macOS Gatekeeper 보안 정책에 의해 차단된 경우 다음 방법으로 해결할 수 있습니다:
1. **Finder 에서 우클릭으로 열기**: 클론 앱(`.app`)을 마우스 우클릭(또는 두 손가락 탭)한 후 **"열기"** 를 선택하고 대화상자에서 "열기"를 클릭합니다.
2. **터미널에서 격리 속성 제거**:
   ```bash
   xattr -cr ~/ATBClone/Apps/<클론이름>.app
   ```

### 6. 클론 앱의 아이콘을 변경하려면 어떻게 하나요?
1. ATBClone 대시보드에서 대상 카드의 **"편집"** 버튼을 클릭합니다.
2. 아이콘 영역에 원하는 `.png` 또는 `.icns` 이미지를 드래그하여 저장합니다.

### 7. 메신저 앱에서 메뉴바 아이콘이나 알림이 작동하지 않을 때 해결 방법은?
일부 메신저 앱은 번들 ID 가 변경되면 알림 센터 등록이 초기화될 수 있습니다:
* macOS 의 **"시스템 설정 ➔ 알림"** 으로 이동하여 클론 앱의 알림 권한이 활성화되어 있는지 확인하십시오.

---

## 🩺 시스템 환경 진단 (Doctor 도구)

환경 의존성과 권한 상태를 점검하려면 내장 Doctor 도구를 사용하십시오:

* **GUI 에서**: 좌측 사이드바의 **"시스템 환경 진단 (Doctor)"** 클릭.
* **CLI 에서**:
  ```bash
  atbclone doctor
  ```

Doctor 도구는 다음 항목을 자동으로 검사합니다:
* [✔] macOS 버전 호환성 (macOS 12+ Monterey / Ventura / Sonoma / Sequoia)
* [✔] Xcode Command Line Tools 및 `codesign` 유틸리티 작동 상태
* [✔] 앱 및 데이터 저장 디렉토리 쓰기 권한
* [✔] 내장 레시피 구문 유효성

---

## 🐞 문제 발견 및 GitHub Issue 보고 절차 (표준 트러블슈팅)

앱 실행 실패 등 이상 현상이 발생하면 다음 절차에 따라 정확한 진단 정보를 수집하여 보고할 수 있습니다:

### 1단계: 메인 화면에서 오류 클론 선택 후 "세부 정보" 클릭
대상 클론 카드를 클릭하고 툴바의 **"세부 정보 (Details)"** 버튼을 누릅니다.

### 2단계: "클론 세부 정보" 에서 진단 리포트 복사
"클론 세부 정보" 대화상자에는 다음 기술 데이터가 자동 수집되어 있습니다:
* 기본 정보 (클론 이름, 전략, Bundle ID, 원본 경로)
* 실행 바이너리 아키텍처 (arm64 / x86_64)
* 주입된 환경 변수 및 프록시 구성
* 최근 크래시 로그 및 실행 로그 요약

하단의 **"진단 정보 복사 (Copy Diagnostic Info)"** 버튼을 클릭합니다.

### 3단계: GitHub Issue 에 제출
1. 브라우저에서 [ATBClone Issues](https://github.com/aitobox/ATBClone/issues) 로 이동합니다.
2. **"New Issue"** 를 클릭하고 "Bug Report" 를 선택합니다.
3. 복사한 진단 정보를 붙여넣고 제출하면 개발팀이 신속히 원인을 분석합니다.

---

## 💬 커뮤니티 및 지원

* **공식 GitHub 저장소**: [https://github.com/aitobox/ATBClone](https://github.com/aitobox/ATBClone)
* **공식 온라인 문서**: [https://clone.aitobox.com](https://clone.aitobox.com)
* **토론 및 질의응답**: [GitHub Discussions](https://github.com/aitobox/ATBClone/discussions)
"""

with open(f"{KO_DIR}/02-advanced-custom-recipes.md", "w", encoding="utf-8") as f:
    f.write(ch02)
print("✓ Created ko/02-advanced-custom-recipes.md")

with open(f"{KO_DIR}/03-under-the-hood-and-internals.md", "w", encoding="utf-8") as f:
    f.write(ch03)
print("✓ Created ko/03-under-the-hood-and-internals.md")

with open(f"{KO_DIR}/04-faq-and-troubleshooting.md", "w", encoding="utf-8") as f:
    f.write(ch04)
print("✓ Created ko/04-faq-and-troubleshooting.md")
