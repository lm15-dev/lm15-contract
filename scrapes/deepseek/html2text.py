#!/usr/bin/env python3
"""Reduce a Docusaurus page (api-docs.deepseek.com) to its article text.

DeepSeek publishes no native Markdown; the <article> element is the only
content-bearing node.  Tags are stripped, block boundaries become newlines,
entities are unescaped.  Nothing is rewritten: a page is the site's words.
"""
import html
import re
import sys

raw = sys.stdin.read()
m = re.search(r"<article.*?</article>", raw, re.S)
text = m.group(0) if m else raw
text = re.sub(r"<script.*?</script>", "", text, flags=re.S)
text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
text = re.sub(r"<br\s*/?>", "\n", text)
text = re.sub(r"</(p|div|h\d|li|tr|pre|table|thead|tbody)>", "\n", text)
text = re.sub(r"</t[dh]>", "\t", text)
text = re.sub(r"<[^>]+>", "", text)
text = html.unescape(text)
text = re.sub(r"[ \t]+\n", "\n", text)
text = re.sub(r"\n\s*\n+", "\n\n", text)
sys.stdout.write(text.strip() + "\n")
