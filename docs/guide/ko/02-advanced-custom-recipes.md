# 제2장: 사용자 정의 레시피 및 기본 매개변수

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
