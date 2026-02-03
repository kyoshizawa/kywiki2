# 第2章 FEXICS API の基本構成

## 2. FEXICS API の基本構成

FEXICS API は、大きく **3 種類** に分類される。

- 業務電文処理用 API  
- 電文編集用 API  
- 制御・運用系 API  

---

## 2.1. 業務電文処理用 API

電文を **送信 / 受信** するための API 群であり、  
以下の 2 つの階層から構成される。

### 業務電文処理 API 一覧

| API 名 | 接続センター | 説明 |
|---|---|---|
| `FX_SendAuth()` | CARDNET | オーソリゼーション要求・アドバイス要求の送信 |
| `FX_CaptureAuth()` | CARDNET | オーソリ済み取引のキャプチャ |
| `FX_SendAndCaptureAuth()` | CARDNET | 売上要求を送信 |
| `FX_GetSeqNum()` | CARDNET | 取引通番の取得 |
| `FX_SendMsg_CN()` | CARDNET | 電文送信 |
| `FX_SendMsg_CF()` | CAFIS | 電文送信 |
| `FX_SendMsg_iD()` | CAFIS (iD) | 電文送信 |
| `FX_ReceiveMsg_CN()` | CARDNET | 電文受信 |
| `FX_ReceiveMsg_CF()` | CAFIS | 電文受信 |
| `FX_ReceiveMsg_iD()` | CAFIS (iD) | 電文受信 |

---

## 2.2. 電文編集用 API

取引項目を指定し、  
各クレジットネットワークで規定された **フォーマットの電文を作成** する API 群。

### 電文編集用 API 一覧

| API 名 | 接続センター | 説明 |
|---|---|---|
| `FX_BuildAuthMsg()` | CARDNET | オーソリ・売上要求電文作成 |
| `FX_BuildAuthMsg_iD()` | CAFIS (iD) | オーソリ・売上要求電文作成 |
| `FX_BuildAdviceMsg()` | CARDNET | アドバイス要求電文作成 |
| `FX_BuildCancelMsg()` | CARDNET | 取消 / 返品電文作成 |
| `FX_BuildCancelMsg_iD()` | CAFIS (iD) | 取消 / 返品電文作成 |
| `FX_BuildCancelMsg2_iD()` | CAFIS (iD) | 取消 / 返品電文作成 |
| `FX_BuildKeyMsg_iD()` | CAFIS (iD) | 鍵配信要求電文作成 |
| `FX_BuildMsg()` | CARDNET | 業務電文作成 |
| `FX_GenPinBlk()` | CARDNET | PIN ブロック生成 |
| `FX_GetField()` | CARDNET | フィールド値取得 |
| `FX_GetLLVAR()` | CARDNET | 可変長（2 桁）取得 |
| `FX_GetLLLVAR()` | CARDNET | 可変長（3 桁）取得 |
| `FX_SetField()` | CARDNET | フィールド値設定 |
| `FX_SetLLVAR()` | CARDNET | 可変長（2 桁）設定 |
| `FX_SetLLLVAR()` | CARDNET | 可変長（3 桁）設定 |

> `FX_GetField` 以降の API は  
> FEXICS Daemon 内部処理で使用される **低レベル電文編集用 API**。  
> 通常は使用しないが、フィールド単位の制御が必要な場合に利用可能。

---

## 2.3. 制御・運用系 API

オペレーターコマンドやシステム制御、  
運用処理・レポート連携に使用される API 群。

### 制御・運用 API 一覧

| API 名 | 接続センター | 説明 |
|---|---|---|
| `FX_OpenSession_CN()` | CARDNET | 業務セッションオープン |
| `FX_OpenSession_CF()` | CAFIS | 業務セッションオープン |
| `FX_OpenSession_iD()` | CAFIS (iD) | 業務セッションオープン |
| `FX_CloseSession()` | 共通 | 業務セッションクローズ |
| `FX_CloseSession_iD()` | CAFIS (iD) | 業務セッションクローズ |
| `FX_Connect()` | 共通 | サインオン電文送信 |
| `FX_Disconnect()` | 共通 | サインオフ電文送信 |
| `FX_CtrlSignOn()` | 共通 | Daemon をサインオン状態にする |
| `FX_CtrlSignOff()` | 共通 | Daemon をサインオフ状態にする |
| `FX_CtrlShutdown()` | 共通 | Daemon 終了 |
| `FX_CtrlRecovery()` | 共通 | 障害回復処理 |
| `FX_IsRunning()` | 共通 | Daemon 起動確認 |
| `FX_IsSignOn()` | 共通 | サインオン状態確認 |
| `FX_IsSwitch()` | 共通 | 内部状態遷移中確認 |
| `FX_IsRecoveryMode()` | 共通 | 障害回復モード確認 |
| `FX_IsReconciled()` | CARDNET | 前日分精査完了確認 |
| `FX_SendSystemCancel_CN()` | CARDNET | 障害取消電文送信 |
| `FX_SendSystemCancel_CF()` | CAFIS | 障害取消電文送信 |
| `FX_SendSystemCancel_iD()` | CAFIS (iD) | 障害取消電文送信 |
| `FX_SendCutOverMsg()` | 共通 | カットオーバー依頼 |
| `FX_SendCutOverMsg_iD()` | CAFIS (iD) | カット対象日付更新 |
| `FX_GetCutDate()` | 共通 | カット対象日付取得 |

※ 接続センターにより動作が異なる API が存在する。  
詳細は **第8章 制御・運用系 API リファレンス** を参照。
