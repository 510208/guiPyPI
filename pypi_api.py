import asyncio
import aiohttp
import subprocess
import sys
import json

# 建立一個 logger
import logging
logger = logging.getLogger(__name__)

class PyPiClient:
    def __init__(self):
        self.base_url = "https://pypi.org/pypi"
        self.package_info_url = f"{self.base_url}/{{}}/json"  # 使用 {{}} 建立一個保留欄位

    async def get_package_info(self, package_name):
        # 取得套件資訊
        async with aiohttp.ClientSession() as session:
            url = self.package_info_url.format(package_name)
            async with session.get(url) as response:
                data = await response.json()
                return data

    async def search_package(self, query):
        # 搜尋套件
        async with aiohttp.ClientSession() as session:
            url = self.package_info_url.format(query)
            async with session.get(url) as response:
                data = await response.json()
#                 print(data)
                return data

    async def install_package(self, package_name):
        # 檢查是否已經安裝該包
        if await self.check_package(package_name):
            return f"套件 {package_name} 已經安裝"
        # 檢查 PyPI 上是否有該套件
        package_info = await self.get_package_info(package_name)
        if not package_info:
            return f"找不到套件 {package_name}"
        # 安裝該包
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        # 檢查是否安裝成功
        if await self.check_package(package_name):
            return f"套件 {package_name} 安裝成功"

    async def check_package(self, package_name):
        logger.info(f"嘗試導入套件：{package_name}")
        try:
            # 嘗試導入套件
            __import__(package_name)
            return True
        except ImportError:
            return False

    async def remove_package(self, package_name):
        # 檢查是否已經安裝該包
        if not await self.check_package(package_name):
            return f"套件 {package_name} 未安裝"
        # 移除該包
        result = subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', package_name, '-y'])
        output = result.stdout.decode('utf-8')
        # 檢查是否移除成功
        if not await self.check_package(package_name):
            logger.info(f"套件 {package_name} 移除成功\n傳回值：\n{output}")
            return f"套件 {package_name} 移除成功\n傳回值：\n{output}"
        
    async def get_local_packages(self):
        # 執行pip list命令並獲取其輸出
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], stdout=subprocess.PIPE)

        # 將輸出轉換為字符串
        output = result.stdout.decode('utf-8')

        # 將輸出分割為行
        lines = output.split('\n')

        # 創建兩個列表來存儲套件名和版本號
        package_names = []
        package_versions = []

        # 跳過前兩行（標題行和分隔行）
        for line in lines[2:]:
            # 分割每一行為包名和版本號
            parts = line.split()
            if len(parts) == 2:
                package, version = parts
                # 將包名和版本號添加到相應的列表中
                package_names.append(package)
                package_versions.append(version)

        # 創建一個字典來存儲結果
        packages = {
            "package": package_names,
            "version": package_versions
        }

        return packages