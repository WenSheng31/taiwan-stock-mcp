from fastmcp import FastMCP
import requests

# 建立 MCP Server
mcp = FastMCP("Taiwan Stock", dependencies=["requests"])


def fetch_stock_data(stock_id: str) -> dict:
    """從證交所 API 獲取股票資料"""
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{stock_id}.tw"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("rtcode") != "0000":
            return {"error": "查詢失敗"}

        stock = data["msgArray"][0]
        price = float(stock.get("z", 0) or 0)
        yesterday = float(stock.get("y", 0) or 0)
        change = price - yesterday
        change_percent = (change / yesterday * 100) if yesterday > 0 else 0

        return {
            "代號": stock.get("c", ""),
            "名稱": stock.get("n", ""),
            "成交價": price,
            "開盤": float(stock.get("o", 0) or 0),
            "最高": float(stock.get("h", 0) or 0),
            "最低": float(stock.get("l", 0) or 0),
            "昨收": yesterday,
            "漲跌": f"{change:+.2f}",
            "漲跌幅": f"{change_percent:+.2f}%",
            "成交量": stock.get("v", "0"),
            "時間": f"{stock.get('d', '')} {stock.get('t', '')}"
        }
    except Exception as e:
        return {"error": f"查詢錯誤: {str(e)}"}


@mcp.tool()
def get_stock_price(stock_id: str) -> str:
    """
    獲取台灣股票即時價格
    :param stock_id: 股票代號 (例如: 2330, 2454, 2303, 2353)
    :return: 股票即時資訊
    """
    data = fetch_stock_data(stock_id)

    if "error" in data:
        return data["error"]

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

    return "\n".join(results) if results else "查詢失敗"


if __name__ == "__main__":
    mcp.run()