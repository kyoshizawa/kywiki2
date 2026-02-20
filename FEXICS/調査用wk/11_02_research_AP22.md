# AP22 (CardnetService) における FEXICS 依存機能調査

## 概要

AP22 ソースコード（22_CardnetService）を調査。AP02 と異なり、**FEXICS を直接呼び出す**実装となっている。
NuGet パッケージ `CreditPaySystem.FexicsAPI_CN` (v4.10.2) を使用。

---

## 1. FEXICS 依存コマンド一覧

| メソッド | 機能 | 対応するAP02コマンド |
|----------|------|---------------------|
| `SignOn()` | 開局（CARDNET接続） | C01 相当 |
| `SignOff()` | 閉局（CARDNET切断） | C02 相当 |
| `GetStatus()` | ステータス取得 | C03 相当 |
| `CutOver()` | 日次更新（締め日更新） | C12 相当 |
| `OnlineAuthICC()` | IC オンラインオーソリ | B22 相当 |
| `OnlineAuthICC_Cancel()` | IC オーソリ取消 | B23 相当 |
| `SystemCancel()` | 障害取消 | B25 相当 |
| `Echo()` | 死活確認（ハートビート） | - |

---

## 2. 通信基盤

### FexicsCNManager（FEXICS 管理クラス）
- **初期化**: `FexicsCNManager.Initialize(dllPath, sessionCount)`
- **終了**: `FexicsCNManager.Destroy()`
- **クライアント生成**:
  - `CreateControlClient()` - 制御系操作用
  - `CreateBusinessClient(mode)` - 業務系操作用
- **イベント**: `OnFexicsMessage` - FEXICS メッセージ受信

### 設定（appsettings.json）
```json
{
  "FexicsBin": "D:\\app\\FEXICS",
  "FexicsSessionNum": 2
}
```

| 設定 | 説明 |
|------|------|
| FexicsBin | FEXICS DLL/ツールのパス |
| FexicsSessionNum | 業務セッション数（0で無効化） |

---

## 3. リポジトリインターフェース

**ファイル**: `Repositories/FexicsServiceRepository.cs`

```csharp
public interface IFexicsServiceRepository
{
    Task<string> CutOver(...);                    // 日次更新
    Task<AuthResult> OnlineAuthICC(...);          // オーソリ
    Task<AuthResult> OnlineAuthICCCancel(...);    // オーソリ取消
    Task<bool> SystemCancel(...);                 // 障害取消
    Task<FexicsConstants.FEXICS_STATUS> IsActive(...);  // ステータス
    Task SignOn(...);                             // 開局
    Task SignOff(...);                            // 閉局
    Task<bool> Echo(...);                         // 死活確認
    // カード有効性キャッシュ関連（14日キャッシュ）
    bool IsExistsCardValidation(...);
    bool RegistCardValidation(...);
    bool UnregistCardValidation(...);
}
```

---

## 4. Action クラスからの利用箇所

### バックエンド（定期・管理操作）
| ファイル | 呼び出し |
|----------|----------|
| `Action/Backend/00_CutDateAction.cs` | `CutOver()` |
| `Action/Backend/05_SignOnAction.cs` | `SignOn()` |
| `Action/Backend/06_SignOffAction.cs` | `SignOff()` |
| `Action/Backend/07_GetStatusAction.cs` | `IsActive()` |
| `Action/Backend/02_SendAuthTotalizeTransactionAction.cs` | `OnlineAuthICC()` |

### オンライン（リアルタイム処理）
| ファイル | 呼び出し |
|----------|----------|
| `Action/Online/01_TransitStartAction.cs` | `OnlineAuthICC()`, `SystemCancel()` |
| `Action/Online/03_OperationUnlockAction.cs` | `OnlineAuthICC()`, `SystemCancel()` |

### ヘルスチェック
| ファイル | 呼び出し |
|----------|----------|
| `HealthAPI.cs` | `IsActive()`, `Echo()`, `RebuildSessionID()` |

---

## 5. FEXICS 固有の処理

### モード切替
```csharp
FexicsConstants.MODE mode = (transaction.Environment == "Test")
    ? FexicsConstants.MODE.TEST
    : FexicsConstants.MODE.PRODUCTION;
```

### 特殊処理
- **Saison カード**: ICC データの 9F02 タグをゼロ設定、9F5A タグ除去
- **AMEX テスト**: `OrgCode21` 設定時に `ORG_CODE_CARDNET` 送信
- **BIT62 データ**: JCB/Saison のカスタムレスポンス解析

---

## 6. エラーハンドリング

### APIException
- FEXICS API 呼び出し失敗時にスロー
- `SystemTraceAuditNo` を保持（障害回復用）

---

## 7. 初期化シーケンス（HostedService.cs）

```csharp
// 起動時
if (_setting.FexicsSessionNum != 0) {
    FexicsCNManager.OnFexicsMessage += handler;
    FexicsCNManager.Initialize(_setting.FexicsBin, _setting.FexicsSessionNum);
}

// 終了時
stoppingToken.Register(() => {
    FexicsCNManager.Destroy();
});
```

---

## 8. AP02 との比較

| 項目 | AP02 (CafisLogic) | AP22 (CardnetService) |
|------|-------------------|----------------------|
| 接続先 | CAFIS | CARDNET |
| FEXICS 利用方式 | TCP 経由（中継サーバ） | DLL 直接呼出し |
| パッケージ | 自前実装（CafisCC） | FexicsAPI_CN (NuGet) |
| セッション管理 | なし | FexicsCNManager |
| iD 関連 | あり（B01, B11, B12） | なし |
| MS 関連 | あり（B16, B17） | なし |
| 銀聯関連 | あり（B20, B21） | なし |
| アドバイス | あり（B24） | なし |
| Echo | なし | あり |

---

## 9. 置き換え対象のまとめ

### 必須機能
1. **開局/閉局** - SignOn, SignOff
2. **ステータス確認** - GetStatus
3. **日次更新** - CutOver
4. **IC オーソリ** - OnlineAuthICC
5. **IC オーソリ取消** - OnlineAuthICC_Cancel
6. **障害取消** - SystemCancel
7. **死活確認** - Echo

### 通信仕様
- **方式**: FEXICS DLL 直接呼出し（ネイティブライブラリ）
- **セッション**: 複数セッション対応（設定可能）
- **モード**: TEST / PRODUCTION 切替

---

*調査日: 2026-02-03*
