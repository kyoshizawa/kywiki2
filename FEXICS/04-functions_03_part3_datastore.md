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
- CAFIS ジャーナル（保留情報）
- CAFIS 通番シーケンス（SQL Server SEQUENCE オブジェクト、テーブルなし）
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

CAFIS との送受信電文を記録するテーブル。INSERT / DELETE のみ行い、更新はしない。
保留状態の有無は `Trn_CafisJournalHold` との LEFT JOIN で判定する（ヒットすれば保留中）。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | BIGINT | ○ | ジャーナルID（主キー、自動採番） |
| CutDate | DATE | ○ | カット対象日付（`Trn_CafisCutDate.CutDate` FK、cascade delete） |
| ConnectCd | VARCHAR(11) | | 処理した接続コード |
| DeliveryCd | VARCHAR(11) | | 仕向先会社コード |
| TerminalNo |VARCHAR(13) | | 端末番号 | 
| SequenceNo | CHAR(6) | | CAFIS 通番 |
| TransactionDateTime | datetime | | 取引日時（レコードの処理日時ではない） |
| Direction | CHAR(1) | ○ | 送受信区分（`S`：送信、`R`：受信） |
| MessageType | VARCHAR(4) | ○ | 電文種別コード |
| RawData | VARBINARY | ○ | 電文生データ（カード情報該当箇所はトランケーション済） |
| ReadableData | NVARCHAR(MAX) | | 電文のわかりやすい表現（フィールド名と値を対応させたJSON形式）※ 負荷軽減のため cli が要求したら解析してセットする |
| SecureDataId | BIGINT | | カード番号の参照番号（SecureDB 上のカードデータ参照ID） |
| ProcessedAt | DATETIME | ○ | 電文送受信日時 |
| Created | DATETIME | | レコード作成日時 |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

### 3.3 CAFIS ジャーナル（保留情報）

テーブル名：`Trn_CafisJournalHold`

回線障害・センタ障害時に保留となった CAFIS ジャーナルを管理するテーブル。
保留が発生したら INSERT、オンライン再開後の再送完了で DELETE する。`Trn_CafisJournal` へのフラグ更新を嫌ってのテーブル構造。

| カラム名 | 型 | NOT NULL | 説明 |
| --- | --- | :---: | --- |
| JournalId | BIGINT | ○ | 保留対象のジャーナルID（主キー、`Trn_CafisJournal.JournalId` FK） |
| Created | DATETIME | | レコード作成日時 |
| Updated | DATETIME | | レコード更新日時 |
| Modifier | VARCHAR(32) | | 最終更新者 |
| RowVersion | TIMESTAMP | | 行バージョン（楽観的排他制御） |

---

### 3.4 CAFIS 通番シーケンス

テーブルなし。SQL Server の **SEQUENCE オブジェクト**で管理する。

- 命名規則：`dbo.CafisSeq_{ConnectCd}`（例：`dbo.CafisSeq_ABC001`）
- 接続コードごとに1オブジェクト。初回使用時に動的 `CREATE SEQUENCE` する
- `NEXT VALUE FOR` はアトミックのため、コンカレント呼び出しでも競合しない
- カット時に `ALTER SEQUENCE ... RESTART WITH 1` でリセットする
- `NO CACHE` 指定により、SQL Server 再起動時の採番飛びを防ぐ

#### 実装サンプル（C# / EF Core）

```csharp
// シーケンス名（ConnectCd は英数字のみ許可してインジェクション対策）
private static string SeqName(string connectCd)
{
    if (!Regex.IsMatch(connectCd, @"^[A-Za-z0-9]+$"))
        throw new ArgumentException("Invalid ConnectCd");
    return $"dbo.CafisSeq_{connectCd}";
}

// 存在しなければ作成
await context.Database.ExecuteSqlRawAsync($"""
    IF NOT EXISTS (
        SELECT 1 FROM sys.sequences
        WHERE schema_id = SCHEMA_ID('dbo') AND name = 'CafisSeq_{connectCd}'
    )
    CREATE SEQUENCE {SeqName(connectCd)}
        AS INT START WITH 1 INCREMENT BY 1
        MINVALUE 1 MAXVALUE 999999 NO CYCLE NO CACHE
    """);

// 採番（競合しない）
var no = await context.Database
    .SqlQueryRaw<int>($"SELECT NEXT VALUE FOR {SeqName(connectCd)}")
    .FirstAsync();
var sequenceNo = no.ToString("D6"); // → "000001"

// カット時にリセット
await context.Database.ExecuteSqlRawAsync(
    $"ALTER SEQUENCE {SeqName(connectCd)} RESTART WITH 1");
```

---

### 3.5 CARDNET カット対象日付

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