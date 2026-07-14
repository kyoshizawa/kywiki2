#!/usr/bin/env python3
"""PDFの内容をページ指定でテキスト化するツール.

PyMuPDF (fitz) を使用して、指定した PDF ファイルの指定ページ範囲を
プレーンテキストとして抽出する。

使用例:
    # 全ページを標準出力へ
    python pdf_to_text.py input.pdf

    # 3ページ目だけ
    python pdf_to_text.py input.pdf -p 3

    # 2〜5ページ
    python pdf_to_text.py input.pdf -p 2-5

    # 1,3,5ページと 10〜12ページ
    python pdf_to_text.py input.pdf -p 1,3,5,10-12

    # ファイルに保存
    python pdf_to_text.py input.pdf -p 2-5 -o out.txt

    # ページ区切りの見出しを付けない
    python pdf_to_text.py input.pdf --no-header

ページ番号は 1 始まり（人間が見るページ番号）で指定する。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit(
        "PyMuPDF がインストールされていません。\n"
        "  pip install pymupdf\n"
        "を実行してください。"
    )


def parse_pages(spec: str, page_count: int) -> list[int]:
    """ページ指定文字列を 0 始まりのページindex リストに変換する.

    spec 例: "3", "2-5", "1,3,5,10-12"
    範囲末尾を省略した "5-" は最終ページまでを表す。
    戻り値は昇順・重複除去済みの 0 始まり index。
    """
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, _, end_s = part.partition("-")
            start = int(start_s) if start_s.strip() else 1
            end = int(end_s) if end_s.strip() else page_count
        else:
            start = end = int(part)
        if start > end:
            start, end = end, start
        for p in range(start, end + 1):
            if 1 <= p <= page_count:
                pages.add(p - 1)  # 0 始まりへ
            else:
                print(
                    f"警告: ページ {p} は範囲外です (1〜{page_count})。スキップします。",
                    file=sys.stderr,
                )
    return sorted(pages)


def extract_text(pdf_path: Path, page_spec: str | None, header: bool) -> str:
    """PDF から指定ページのテキストを抽出して連結文字列で返す."""
    with fitz.open(pdf_path) as doc:
        page_count = doc.page_count
        if page_spec:
            indices = parse_pages(page_spec, page_count)
            if not indices:
                sys.exit("抽出対象のページがありません。")
        else:
            indices = list(range(page_count))

        chunks: list[str] = []
        for idx in indices:
            text = doc[idx].get_text()
            if header:
                chunks.append(f"===== ページ {idx + 1} / {page_count} =====\n{text}")
            else:
                chunks.append(text)
        return "\n".join(chunks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PDFの内容をページ指定でテキスト化するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pdf", type=Path, help="入力PDFファイルのパス")
    parser.add_argument(
        "-p",
        "--pages",
        help='ページ指定 (例: "3", "2-5", "1,3,5,10-12")。省略時は全ページ。1始まり。',
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="出力先テキストファイル。省略時は標準出力。",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="ページ区切りの見出しを付けない。",
    )
    args = parser.parse_args(argv)

    if not args.pdf.is_file():
        sys.exit(f"ファイルが見つかりません: {args.pdf}")

    text = extract_text(args.pdf, args.pages, header=not args.no_header)

    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"書き出しました: {args.output} ({len(text)} 文字)", file=sys.stderr)
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
