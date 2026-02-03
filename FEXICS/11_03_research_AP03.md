# AP03 (CAFIS-CONNECT) の機能分析

## 概要

AP03 ソースコード（03_CAFIS-CONNECT）を調査。Java で実装。
AP02 と FEXICS の間に位置する**通信制御レイヤー**で、単純な中継ではなく、
セッション管理・障害回復・電文変換・監視など多くの機能を担っている。

---

## 1. アーキテクチャ

```
AP02 --TCP:7000--> [TcpServer] --> [RequestDispatcher] --> [Action] --> [FexicsAPI(JNI)] --> FEXICS
                                                                              ↕
                                                              [DaemonEventChkThread] (常時監視)
                                                              [CafisControl] (接続制御)
```

### 主要クラス

| クラス | ファイル | 役割 |
|--------|----------|------|
| TcpServer | TcpServer.java | TCP:7000 で AP02 からの接続受付 |
| RequestDispatcher | RequestDispatcher.java | リクエスト振り分け、シリアライズ |
| RequestExecute | RequestExecute.java | スレッドプールでのリクエスト処理 |
| CafisCtrlManager | CafisCtrlManager.java | 接続状態管理（グローバル） |
| CafisControl | CafisControl.java | 接続ライフサイクル制御 |
| DaemonEventChkThread | DaemonEventChkThread.java | FEXICS デーモンイベント監視 |
| FexicsAPI | FexicsAPI.java | FEXICS ネイティブライブラリの JNI ラッパー |

---

## 2. 隠れた機能（単純中継を超える部分）

### 2.1 セッション管理

- **セッションプール**: リクエストスレッド数 + イベント監視 + 制御用の複数セッションを管理
- **セッション再生成**: エラー時に全セッションを閉じて再オープンする自動リカバリ
- **updateSesId ロジック**: 業務処理の完了を待ってからセッション再生成を実行

### 2.2 接続状態マシン

- **状態**: DISCONNECTED, CONNECTED, CONNECTING, DISCONNECTING, ERROR
- **排他制御**: connectLock による競合防止
- **リカバリ**: `fxCtrlRecovery()` による制御された再接続

### 2.3 デーモンイベント監視（DaemonEventChkThread）

常駐スレッドで FEXICS デーモンを継続監視：
- **SIGNON** イベント → 接続処理
- **SIGNOFF** イベント → 切断処理
- **ERR_ALL_SESSION** → セッション再生成
- **ERR_CD_SOCKET** → ソケットエラー時の自動回復
- **タイムアウト** → 例外なし、待機継続
- エラー時の suspend interval（デフォルト10秒）

### 2.4 電文変換パイプライン

各 Action で以下の変換処理を実施：
1. クライアントリクエストのバリデーション
2. **リクエスト編集** - AP02 形式 → CAFIS 電文形式（`*ReqEditor.edit()`）
3. FEXICS への送信（`fxSendMsg`）/ 受信（`fxRecvMsg`）
4. **レスポンス解析** - CAFIS 応答の検証（`*Analyze.analyze()`）
5. **レスポンス編集** - CAFIS 形式 → AP02 形式（`*ResEditor.edit()`）

### 2.5 障害取消（SystemCancel）の自動送信

- FEXICS への送信成功後にエラーが発生した場合、**自動的に SystemCancel を送信**
- 日付(YYMMDD)、端末ID、端末シーケンスを使用
- AuthAction, AuthCancelAction, ICC系 Action で実装

### 2.6 業務処理カウント・同期制御

- **bizActionNum**: 処理中トランザクション数をカウント（volatile）
- **waitBizActionEnd()**: 切断前に全業務処理完了を最大60秒待機
- **connectLock**: 開局/閉局時に業務処理との排他制御

---

## 3. リクエストタイプ一覧（18種）

| タイプ | Action クラス | 機能 |
|--------|--------------|------|
| B01 | AccessKeyGetAction | アクセスキー取得 |
| B10 | CafisOpenAction | 開局 |
| B11 | iDOnlineAuthAction | iD オーソリ |
| B12 | iDOnlineAuthCancelAction | iD オーソリ取消 |
| B16 | AuthAction | オンラインオーソリ |
| B17 | AuthCancelAction | オーソリ取消 |
| B20 | UnionPayAuthAction | 銀聯オーソリ |
| B21 | UnionPayAuthCancelAction | 銀聯オーソリ取消 |
| B22 | ICCAuthAction | IC オーソリ |
| B23 | ICCAuthCancelAction | IC オーソリ取消 |
| B24 | AdviceAction | アドバイス |
| B25 | SystemCancelAction | 障害取消 |
| B30 | AuthUriageAction | 売上オーソリ |
| B31 | AuthUriageCancelAction | 売上オーソリ取消 |
| B32 | ICCAuthUriageAction | IC 売上オーソリ |
| B33 | ICCAuthUriageCancelAction | IC 売上オーソリ取消 |
| - | CutDateGetAction | 締め日取得 |
| - | CutDateUpdateAction | 締め日更新 |
| - | CafisStsGetAction | ステータス取得 |
| - | CafisCloseAction | 閉局 |

**注意**: B30〜B33（売上オーソリ系）は AP02 の調査では確認されなかった。

---

## 4. FEXICS API（JNI ネイティブ）

| メソッド | 機能 |
|----------|------|
| `fxOpenSession()` | セッション作成 |
| `fxCloseSession()` | セッション終了 |
| `fxConnect()` | FEXICS 接続確立 |
| `fxDisconnect()` | FEXICS 切断 |
| `fxSendMsg()` | 電文送信 |
| `fxRecvMsg()` | 電文受信（ブロッキング） |
| `fxSendCutOverMsg()` | 締め日更新送信 |
| `fxGetCutDate()` | 締め日取得 |
| `fxSendSystemCancel()` | 障害取消送信 |
| `fxCtrlRecovery()` | リカバリシーケンス実行 |

---

## 5. TCP 通信仕様

### AP02 → AP03（受信側）
- **ポート**: 7000
- **ヘッダ**: 5バイト（10進数のコンテンツ長） + 2バイト（CRLF）
- **ボディ**: Key=Value 形式、CRLF 区切り

### AP03 → FEXICS（送信側）
- **方式**: ネイティブライブラリ（JNI）経由
- **最大電文サイズ**: 4096バイト
- **内容**: センターID、シーケンス、仕向会社コード、被仕向会社コード、電文種別、電文データ

---

## 6. 設定（cafis-config.properties）

| 設定 | 内容 | デフォルト |
|------|------|-----------|
| CONNECT_CD | CAFIS 接続コード | MCK-FDEV01 |
| REQUEST_PORT | TCPリスンポート | 7000 |
| REQUEST_THREAD_NUM | ワーカースレッド数 | 5 |
| SHIMUKE_KAISYA_CODE | 仕向会社コード | 11桁 |
| HISHIMUKE_KAISYA_CODE | 被仕向会社コード | 11桁 |
| MAKER_CD | メーカーコード | 011 |
| KEY_VERSION_NO | 暗号鍵バージョン | - |
| BIZ_END_MAX_WAIT_TIME | 業務終了最大待機時間 | 60秒 |
| BIZ_END_CHECK_INTERVAL | 業務終了チェック間隔 | 100ms |
| ERR_EVENT_THREAD_SUSPEND_INTERVAL | エラー時待機時間 | 10秒 |

---

## 7. ロギング

**2系統のログ出力**:

| ログ | ファイル | 内容 |
|------|----------|------|
| メッセージログ | msg.log | 運用ログ（debug/info/warn/error） |
| ジャーナルログ | jnl.log | 電文の監査証跡 |

- 日次ローテーション
- 保持期間: 92日

---

## 8. 新システムへの移行で考慮すべき点

### Routing Engine / Gateway Service に引き継ぐべき機能

| 機能 | 重要度 | 備考 |
|------|--------|------|
| セッションプール管理 | 高 | セッション枯渇時の自動再生成を含む |
| デーモンイベント監視相当の仕組み | 高 | 接続先の状態変化を検知する必要がある |
| 電文変換パイプライン | 高 | 18種の Action に対応する変換ロジック |
| 障害取消の自動送信 | 高 | 金融整合性に直結 |
| 業務処理カウント・グレースフルシャットダウン | 中 | 処理中電文のロスト防止 |
| 接続状態マシン | 中 | 排他制御を含む |
| 2系統ログ（運用＋監査） | 中 | PCI DSS 要件 |
| 7バイトヘッダの TCP プロトコル | 低 | AP02 側を変更するなら仕様変更可能 |

### AP02 調査との差分

- **B30, B31, B32, B33**（売上オーソリ系）は AP03 に Action が存在するが、**未使用のため対象外**

---

*調査日: 2026-02-03*
