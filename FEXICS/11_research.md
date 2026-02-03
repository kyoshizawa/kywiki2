# AP02 (CafisLogic) における FEXICS 依存機能調査

## 概要

AP02 ソースコード（02_CafisLogic）を調査し、FEXICS（CAFIS-CONNECT）に依存する機能を特定した。
コード上では `CafisFacade` クラスを通じて FEXICS サーバー（127.0.0.1:7000）と TCP 通信を行っている。

---

## 1. FEXICS 依存コマンド一覧

### B系コマンド（決済処理）

| コマンド | クラス名 | 機能 |
|----------|----------|------|
| B01 | B01_GetAccessKey | iD アクセスキー取得 |
| B11 | B11_iDOnlineAuth | iD オンラインオーソリ |
| B12 | B12_iDOnlineAuthCancel | iD オーソリ取消 |
| B16 | B16_OnlineAuth | MS（磁気）オンラインオーソリ |
| B17 | B17_OnlineAuthCancel | MS オーソリ取消 |
| B20 | B20_UnionpayOnlineAuth | 銀聯オンラインオーソリ |
| B21 | B21_UnionpayOnlineAuthCancel | 銀聯オーソリ取消 |
| B22 | B22_OnlineAuthIC | IC オンラインオーソリ |
| B23 | B23_OnlineAuthICCancel | IC オーソリ取消 |
| B24 | B24_Advice | IC アドバイス送信 |
| B25 | B25_SystemCancel | 障害取消 |

### C系コマンド（システム制御）

| コマンド | クラス名 | 機能 |
|----------|----------|------|
| C01 | C01_CafisOpen | 開局（ログイン） |
| C02 | C02_CafisClose | 閉局（ログアウト） |
| C03 | C03_GetCafisStatus | ステータス取得 |
| C11 | C11_GetCutDate | 締め日取得 |
| C12 | C12_UpdateCutDate | 締め日更新 |

---

## 2. 通信基盤

### CafisFacade（エントリポイント）
- **ファイル**: `CafisCommand/CafisFacade.cs`
- **役割**: 全 FEXICS コマンドの静的ファサード
- **初期化**: `CafisFacade.Initialize(IPEndPoint)` で接続先を設定

### CafisCommand<T, TResponse>（コマンド基底クラス）
- **ファイル**: `CafisCommand/Base/CafisCommand.cs`
- **役割**: リクエスト/レスポンスのシリアライズ、タイムアウト制御
- **タイムアウト**: 90秒
- **エンコーディング**: Shift_JIS

### CafisCC（TCP通信）
- **ファイル**: `CafisCommand/Base/CafisCC.cs`
- **役割**: FEXICS サーバーとの TCP ソケット通信
- **主要メソッド**:
  - `Open(IPEndPoint)` - 接続確立
  - `SendRequest(byte[], int)` - 送受信
  - `Close()` - 切断

### 電文フォーマット
- ヘッダ: 7バイト（メッセージ長） + CRLF
- ボディ: Key=Value 形式、CRLF 区切り

---

## 3. Action クラスからの利用箇所

### CAFIS システム操作
| ファイル | 呼び出し |
|----------|----------|
| `Action/CAFIS/OpenAction.cs` | `C01_CafisOpen()` |
| `Action/CAFIS/CloseAction.cs` | `C02_CafisClose()` |
| `Action/CAFIS/StatAction.cs` | `C03_GetCafisStatus()` |
| `Action/CAFIS/CutDateUpdateAction.cs` | `C12_UpdateCutDate()` |
| `Action/CAFIS/AuthSystemCancelAction.cs` | `B25_SystemCancel()` |

### iD 決済
| ファイル | 呼び出し |
|----------|----------|
| `Action/iD/GetAccessKeyAction.cs` | `B01_GetAccessKey()` |
| `Action/iD/OnlineAuthiDForPaymentAction.cs` | `B11_iDOnlineAuth()` |
| `Action/iD/OnlineAuthiDForRepaymentAction.cs` | `B12_iDOnlineAuthCancel()` |
| `Action/iD/UpdateAccessKeyVersionAction.cs` | `B01_GetAccessKey()` |

### MS（磁気）決済
| ファイル | 呼び出し |
|----------|----------|
| `Action/MS/OnlineAuthCrForPaymentAction.cs` | `B16_OnlineAuth()` |
| `Action/MS/OnlineAuthCrForRePaymentAction.cs` | `B17_OnlineAuthCancel()` |

### IC カード決済
| ファイル | 呼び出し |
|----------|----------|
| `Action/IC/OnlineAuthICCForPaymentAction.cs` | `B22_OnlineAuthIC()` |
| `Action/IC/OnlineAuthICCForRePaymentAction.cs` | `B23_OnlineAuthICCancel()` |
| `Action/IC/PaymentICCAction.cs` | `B24_Advice()` |

### 銀聯決済
| ファイル | 呼び出し |
|----------|----------|
| `Action/Ginren/OnlineAuthGinrenForPaymentAction.cs` | `B20_UnionpayOnlineAuth()` |
| `Action/Ginren/OnlineAuthGinrenForRePaymentAction.cs` | `B21_UnionpayOnlineAuthCancel()` |

### SecureIC 決済
| ファイル | 呼び出し |
|----------|----------|
| `Action/SecureIC/OnlineAuthSecureAction.cs` | `B22_OnlineAuthIC()` |
| `Action/SecureIC/OnlineAuthSecureRepaymentAction.cs` | `B23_OnlineAuthICCancel()` |
| `Action/SecureIC/PaymentICCSecureAction.cs` | `B24_Advice()` |

### Global Action
| ファイル | 呼び出し |
|----------|----------|
| `Action_Global/Credit/OnlineAuthAction.cs` | `B22_OnlineAuthIC()` |
| `Action_Global/Credit/OnlineAuthCancelAction.cs` | `B23_OnlineAuthICCancel()` |
| `Action_Global/System/IsAliveAction.cs` | `C03_GetCafisStatus()` |
| `Action_Global/Term/PaymentModel/01_CrPaymentModel.cs` | `B24_Advice()` |

---

## 4. エラーハンドリング

### CafisAccessException
- **ファイル**: `CafisCommand/CafisAccessException.cs`
- **エラーコード**:
  - `RA-CA01`: 接続失敗
  - `RA-CA02`: 不正なレスポンス形式
  - `RA-CA03`: リクエストタイムアウト
  - `RA-CA04`: FEXICS エラーレスポンス
  - `RA-CA05`: FEXICS タイムアウトエラー
  - `RA-CA99`: 予期しないエラー

---

## 5. 設定

### appsettings.json
```json
{
  "CafisConnectCd": "2s30809-0001",
  "CafisConnectPort": 7000
}
```

### 初期化（ProcessManager.cs）
```csharp
CafisFacade.Initialize(new IPEndPoint(IPAddress.Parse("127.0.0.1"), setting.CafisConnectPort));
```

---

## 6. 置き換え対象のまとめ

新システム（Routing Engine + Gateway Service）で実装が必要な機能：

### 必須機能
1. **TCP リスナー** - AP02 からの接続受付
2. **開局/閉局** - C01, C02
3. **ステータス確認** - C03
4. **オーソリ** - B11, B16, B22
5. **オーソリ取消** - B12, B17, B23
6. **アドバイス** - B24
7. **障害取消** - B25
8. **アクセスキー取得** - B01（iD用）
9. **日次更新（締め日管理）** - C11, C12

### 対象外（実装あり・未使用）
- **銀聯オーソリ** - B20, B21（ほぼ使用されていないため対象外予定）

### 通信仕様
- プロトコル: TCP
- エンコーディング: Shift_JIS
- タイムアウト: 90秒
- 電文形式: 7バイトヘッダ + Key=Value ペア

---

*調査日: 2026-02-03*
