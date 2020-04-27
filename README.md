# Scrapers
スクレイピング用のスクリプト集

## TweetsScraper
自分のアカウントがフォローしている人をたどって、対話を集めます

## YouTubeCommentScraper
youtube の livechat を集めます

# utils
スクレイピングしたデータを整形する用

## convert_tsv.py
json 形式で保存したデータを \t 区切りへ変換する
話者は、特殊トークンで識別する

## remove_similar_text.py
YouTubeのコメントで、被りや、連続する似たコメントを削除するこで、データ量を減らします

# 特殊トークン