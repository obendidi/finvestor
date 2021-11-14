import json
from typing import Any, Dict


def parse_quote_summary(html_content: str) -> Dict[str, Any]:
    data = json.loads(
        html_content.split("root.App.main =")[1]
        .split("(this)")[0]
        .split(";\n}")[0]
        .strip()
        .replace("{}", "null")
    )
    quote_symmary_store = (
        data.get("context", {})
        .get("dispatcher", {})
        .get("stores", {})
        .get("QuoteSummaryStore")
    )

    return quote_symmary_store
