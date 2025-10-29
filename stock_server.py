from fastmcp import FastMCP
import requests
import urllib3

# 停用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mcp = FastMCP("Taiwan Stock", dependencies=["requests"])

@mcp.tool()
def get_stock_price(stock_id: str) -> str:
    """
    獲取台灣股票即時價格
    :param stock_id: 股票代號 (例如: 2330, 2454, 2303, 2353)
    :return: 股票即時資訊
    """
    stock_id = stock_id.strip().zfill(4)
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{stock_id}.tw"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://mis.twse.com.tw/',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        return response.text
    except Exception as e:
        return f"錯誤: {str(e)}"

if __name__ == "__main__":
    mcp.run()
