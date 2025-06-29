# ProxySpider

## 项目简介
ProxySpider 是一个代理IP管理工具，它负责自动化地获取、测试、存储和管理代理IP，确保您始终拥有可用的优质代理资源。

## 功能特性
*   **代理获取**：从 `checkerproxy.net` 等来源获取最新的代理IP。
*   **连通性测试**：使用多线程并发测试代理的可用性和响应时间，确保代理的质量。
*   **数据库管理**：使用 SQLite 数据库存储和管理代理IP，支持代理的创建、插入、查询、更新和删除操作。
*   **IP评分**：根据代理的连通性和响应时间，对IP进行评分，优先使用优质代理。
*   **重复IP删除**：自动识别并删除数据库中的重复代理IP。
*   **过期IP删除**：定期清理数据库中已过期的代理IP。
*   **优质IP导出**：支持将测试合格的优质代理IP导出，方便其他应用使用。

## 安装
本项目依赖于 `requests` 和 `loguru` 库。您可以通过以下命令安装它们：

```bash
pip install -r requirements.txt
```

## 使用方法
要运行 ProxySpider，请直接执行 `main.py` 文件：

```bash
python main.py
```

程序将自动开始获取、测试和管理代理IP。

## 文件结构
*   [`main.py`](main.py): 项目的主程序入口，负责协调代理的获取、测试和数据库操作的整个流程。
*   [`proxy.py`](proxy.py): 专门用于从 `checkerproxy.net` 等指定来源获取代理IP的模块。
*   [`ProxyTester.py`](ProxyTester.py): 代理连通性测试工具，利用多线程并发机制高效测试代理的可用性和响应时间。
*   [`database_control.py`](database_control.py): 数据库操作模块，封装了对 SQLite 数据库中代理IP的创建、插入、查询、更新、删除和导出等操作。
*   [`cal_time.py`](cal_time.py): 时间计算工具，提供获取今天、昨天和明天日期等功能，用于处理与时间相关的逻辑。
*   [`convert.py`](convert.py): 数据转换工具，负责将代理测试结果转换为数据库可接受的格式，并根据测试结果计算代理IP的质量分数。
*   [`requirements.txt`](requirements.txt): 列出了项目所需的所有Python依赖库。

## 许可证
本项目采用 MIT 许可证。