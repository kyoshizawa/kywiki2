## データストア

### 1. 保存・定義場所

#### サーバ

- 既存サーバ `secdb0x` を使用する。

#### カタログ

- 新規カタログとして、以下を定義する

    | カタログ名 | 用途 |
    | --- | --- |
    | Journal | Gateway 専用のデータストア |

#### 保持期間の定義

ジャーナルレコードは保存から３０日保持する。

#### セキュリティ配慮

- カードストライプ情報は本カタログに保存しないこと。
  代替情報として SecureDB で既に保存済のカードデータ参照IDを保持する。

- 通信の生データ情報など、形式上特定の位置にカード情報が存在する場合は、
  該当箇所をマスク処理でトランケーションした上で保存する。

### 2. テーブル構造一覧

- CAFIS カット対象日付
- CAFIS ジャーナル
- CAFIS 最新通番情報
- CARDNET カット対象日付
- CARDNET ジャーナル
- CARDNET 最新通番情報
- CARDNET KEK

#### リレーション

![図](./img/datastore_1-1.png)




#### メモ

・保留電文フラグ
・カード番号の参照番号
・生データとわかりやすい表現

---

## 3. テーブル詳細

### 3.1 CAFIS カット対象日付

テーブル名：`Trn_CafisCutDate`

CAFIS の日次バッチ処理において、カット（締め）処理の対象となる日付を管理するテーブル。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| CutDate | DATE | ○ | カット対象日付（主キー） |
| Status | CHAR(1) | ○ | 処理状態（`0`：未処理、`1`：処理中、`2`：完了） |
| DeleteDate | DATE | ○ | 削除予定日（`CutDate` + 30日）。カット日付更新コマンド実行時にこの日付に達したレコードをジャーナルごと削除する |
| Created | DATETIME | | レコード作成日時 |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

### 3.2 CAFIS ジャーナル

テーブル名：`Trn_CafisJournal`

CAFIS との送受信電文を記録するテーブル。カード番号の生値は保存しない。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | BIGINT | ○ | ジャーナルID（主キー、自動採番） |
| CutDate | DATE | ○ | カット対象日付（`Trn_CafisCutDate.CutDate` FK、cascade delete） |
| SequenceNo | CHAR(6) | ○ | CAFIS 通番 |
| Direction | CHAR(1) | ○ | 送受信区分（`S`：送信、`R`：受信） |
| MessageType | VARCHAR(10) | ○ | 電文種別コード |
| RawData | VARBINARY | ○ | 電文生データ（カード情報該当箇所はトランケーション済） |
| ReadableData | NVARCHAR(MAX) | | 電文のわかりやすい表現（フィールド名と値を対応させたJSON形式）※ 負荷軽減のため cli が要求したらセットする |
| SecureDataId | BIGINT | | カード番号の参照番号（SecureDB 上のカードデータ参照ID） |
| HoldFlag | CHAR(1) | ○ | 保留電文フラグ（`0`：通常、`1`：保留中） |
| ProcessedAt | DATETIME | ○ | 電文送受信日時 |
| Created | DATETIME | | レコード作成日時 |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

### 3.4 CARDNET カット対象日付

テーブル名：`Trn_CardnetCutDate`

CARDNET の日次バッチ処理において、カット（締め）処理の対象となる日付を管理するテーブル。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| CutDate | DATE | ○ | カット対象日付（主キー） |
| Status | CHAR(1) | ○ | 処理状態（`0`：未処理、`1`：処理中、`2`：完了） |
| DeleteDate | DATE | ○ | 削除予定日（`CutDate` + 30日）。カット日付更新コマンド実行時にこの日付に達したレコードをジャーナルごと削除する |
| Created | DATETIME | | レコード作成日時 |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |
