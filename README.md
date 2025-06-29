# ProxySpider

## 项目简介
ProxySpider 是一个代理IP管理工具，它负责自动化地获取、测试、存储和管理代理IP，确保您始终拥有可用的优质代理资源。

## Project Introduction
ProxySpider is a proxy IP management tool designed to automate the acquisition, testing, storage, and management of proxy IPs, ensuring you always have access to high-quality, available proxy resources.

## 功能特性
*   **代理获取**：从 `checkerproxy.net` 等来源获取最新的代理IP。
*   **连通性测试**：使用多线程并发测试代理的可用性和响应时间，确保代理的质量。
*   **数据库管理**：使用 SQLite 数据库存储和管理代理IP，支持代理的创建、插入、查询、更新和删除操作。
*   **IP评分**：根据代理的连通性和响应时间，对IP进行评分，优先使用优质代理。
*   **重复IP删除**：自动识别并删除数据库中的重复代理IP。
*   **过期IP删除**：定期清理数据库中已过期的代理IP。
*   **优质IP导出**：支持将测试合格的优质代理IP导出，方便其他应用使用。

## Features
*   **Proxy Acquisition**: Automatically fetches the latest proxy IPs from sources like `checkerproxy.net`.
*   **Connectivity Testing**: Utilizes multi-threaded concurrency to test proxy availability and response times, ensuring proxy quality.
*   **Database Management**: Stores and manages proxy IPs using an SQLite database, supporting creation, insertion, querying, updating, and deletion operations.
*   **IP Scoring**: Assigns scores to IPs based on their connectivity and response time, prioritizing high-quality proxies.
*   **Duplicate IP Removal**: Automatically identifies and removes duplicate proxy IPs from the database.
*   **Expired IP Deletion**: Periodically cleans up expired proxy IPs from the database.
*   **Premium IP Export**: Supports exporting tested and qualified premium proxy IPs for use by other applications.

## 安装
本项目依赖于 `requests` 和 `loguru` 库。您可以通过以下命令安装它们：

```bash
pip install -r requirements.txt
```

## Installation
This project depends on the `requests` and `loguru` libraries. You can install them using the following command:

```bash
pip install -r requirements.txt
```

## 使用方法
要运行 ProxySpider，请直接执行 `main.py` 文件：

```bash
python main.py
```

程序将自动开始获取、测试和管理代理IP。

## Usage
To run ProxySpider, execute the `main.py` file directly:

```bash
python main.py
```

The program will automatically start acquiring, testing, and managing proxy IPs.

## 文件结构
*   [`main.py`](main.py): 项目的主程序入口，负责协调代理的获取、测试和数据库操作的整个流程。
*   [`proxy.py`](proxy.py): 专门用于从 `checkerproxy.net` 等指定来源获取代理IP的模块。
*   [`ProxyTester.py`](ProxyTester.py): 代理连通性测试工具，利用多线程并发机制高效测试代理的可用性和响应时间。
*   [`database_control.py`](database_control.py): 数据库操作模块，封装了对 SQLite 数据库中代理IP的创建、插入、查询、更新、删除和导出等操作。
*   [`cal_time.py`](cal_time.py): 时间计算工具，提供获取今天、昨天和明天日期等功能，用于处理与时间相关的逻辑。
*   [`convert.py`](convert.py): 数据转换工具，负责将代理测试结果转换为数据库可接受的格式，并根据测试结果计算代理IP的质量分数。
*   [`requirements.txt`](requirements.txt): 列出了项目所需的所有Python依赖库。

## File Structure
*   [`main.py`](main.py): The main program entry point, responsible for coordinating the entire process of proxy acquisition, testing, and database operations.
*   [`proxy.py`](proxy.py): A module specifically designed to fetch proxy IPs from specified sources like `checkerproxy.net`.
*   [`ProxyTester.py`](ProxyTester.py): A proxy connectivity testing tool that efficiently tests proxy availability and response times using a multi-threaded concurrent mechanism.
*   [`database_control.py`](database_control.py): The database operation module, encapsulating operations such as creation, insertion, querying, updating, deletion, and exporting of proxy IPs in the SQLite database.
*   [`cal_time.py`](cal_time.py): A time calculation utility that provides functions for getting today's, yesterday's, and tomorrow's dates, used for handling time-related logic.
*   [`convert.py`](convert.py): A data conversion tool responsible for converting proxy test results into a database-acceptable format and calculating the quality score of proxy IPs based on test results.
*   [`requirements.txt`](requirements.txt): Lists all Python dependency libraries required by the project.

## 许可证
本项目采用 MIT 许可证。

## License
This project is licensed under the MIT License.

## 如何贡献

非常欢迎并感谢所有形式的贡献！如果您有兴趣改进 ProxySpider，无论是提交 Bug 报告、功能请求，还是直接提交 Pull Request，我们都非常欢迎。

### 提交 Bug 报告或功能请求

*   如果您发现任何 Bug 或有新的功能想法，请在 GitHub 上提交一个 Issue。
*   请尽可能详细地描述问题或功能，包括重现步骤、预期行为和实际行为（针对 Bug）。

### 提交 Pull Request

*   在提交 Pull Request 之前，请确保您的代码符合规范。
*   对于新功能或 Bug 修复，请尽量包含相应的测试用例，以确保代码的稳定性和正确性。
*   请确保您的 Pull Request 描述清晰，说明您所做的更改以及这些更改的目的。

感谢您的贡献，帮助我们让 ProxySpider 变得更好！

## How to Contribute

All forms of contributions are highly welcome and appreciated! If you are interested in improving ProxySpider, whether by submitting bug reports, feature requests, or directly submitting a Pull Request, we warmly welcome you.

### Submitting Bug Reports or Feature Requests

*   If you find any bugs or have new feature ideas, please submit an Issue on GitHub.
*   Please describe the problem or feature as detailed as possible, including reproduction steps, expected behavior, and actual behavior (for bugs).

### Submitting Pull Requests

*   Before submitting a Pull Request, please ensure your code adheres to the coding standards.
*   For new features or bug fixes, please try to include corresponding test cases to ensure code stability and correctness.
*   Please ensure your Pull Request description is clear, explaining the changes you've made and their purpose.

Thank you for your contributions, helping us make ProxySpider even better!