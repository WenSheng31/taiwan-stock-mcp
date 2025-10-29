from fastmcp import FastMCP
import requests

# 建立 MCP Server
mcp = FastMCP("Taiwan Stock", dependencies=["requests"])


def fetch_stock_data(stock_id: str) -> dict:
    """從證交所 API 獲取股票資料"""
    stock_id = stock_id.strip().zfill(4)

    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{stock_id}.tw"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://mis.twse.com.tw/',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("rtcode") != "0000":
            return {"error": f"API 錯誤碼: {data.get('rtcode')}"}

        if not data.get("msgArray"):
            return {"error": f"查無股票 {stock_id}"}

        stock = data["msgArray"][0]

        def safe_float(value, default=0.0):
            try:
                return float(value) if value and value != '-' else default
            except:
                return default

        price = safe_float(stock.get("z"))
        yesterday = safe_float(stock.get("y"))
        change = price - yesterday
        change_percent = (change / yesterday * 100) if yesterday > 0 else 0

        return {
            "代號": stock.get("c", ""),
            "名稱": stock.get("n", ""),
            "成交價": price,
            "開盤": safe_float(stock.get("o")),
            "最高": safe_float(stock.get("h")),
            "最低": safe_float(stock.get("l")),
            "昨收": yesterday,
            "漲跌": f"{change:+.2f}",
            "漲跌幅": f"{change_percent:+.2f}%",
            "成交量": stock.get("v", "0"),
            "時間": f"{stock.get('d', '')} {stock.get('t', '')}"
        }
    except Exception as e:
        return {"error": f"請求失敗: {str(e)}"}


@mcp.tool()
def get_stock_price(stock_id: str) -> str:
    """
    獲取台灣股票即時價格
    :param stock_id: 股票代號 (例如: 2330, 2454, 2303, 2353)
    :return: 股票即時資訊
    """
    data = fetch_stock_data(stock_id)
    if "error" in data:
        return f"❌ {data['error']}"

    return f"""
【{data['名稱']} ({data['代號']})】
成交價: {data['成交價']} 元
漲跌: {data['漲跌']} ({data['漲跌幅']})
開盤: {data['開盤']} | 最高: {data['最高']} | 最低: {data['最低']}
成交量: {data['成交量']} 股
更新時間: {data['時間']}
"""


@mcp.tool()
def compare_stocks(stock_ids: str) -> str:
    """
    比較多檔股票價格
    :param stock_ids: 股票代號，用逗號分隔 (例如: 2330,2454,2303,2353)
    :return: 多檔股票比較資訊
    """
    ids = [sid.strip() for sid in stock_ids.split(",")]
    results = []
    for stock_id in ids:
        data = fetch_stock_data(stock_id)
        if "error" not in data:
            results.append(
                f"{data['名稱']}({data['代號']}): {data['成交價']}元 {data['漲跌']} ({data['漲跌幅']})"
            )
        else:
            results.append(f"{stock_id}: {data['error']}")
    return "\n".join(results) if results else "全部查詢失敗"


if __name__ == "__main__":
    mcp.run()
