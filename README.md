# arXiv Paper Filter

一个轻量级的工具，使用 OpenAI 兼容的 API 根据您的研究兴趣自动筛选每日 arXiv 论文更新。

## 功能特点

- 自动获取每日 arXiv RSS feed 更新
- 使用 LLM 根据您的研究兴趣筛选论文
- 提供个性化的论文推荐
- 生成 RSS feed，方便订阅和阅读
- 简单易用

## RSS Feed 订阅

您可以通过以下方式订阅筛选后的论文：

1. 访问 `https://yourusername.github.io/arxiv_filter/feed.xml`
2. 将链接添加到您的 RSS 阅读器中
3. 每天早上 10:00（北京时间）自动获取更新

## 使用方法

### 1. Fork 本仓库

点击本仓库右上角的 "Fork" 按钮，将本仓库复制到您自己的 GitHub 账户下。

### 2. 配置 GitHub Secrets

在您 Fork 后的仓库中，进入 "Settings" -> "Secrets and variables" -> "Actions"，添加以下 Repository secrets：

-   `API_KEY`: 您用于调用 OpenAI 兼容 API 的密钥。
-   `MODEL_NAME`: 您希望使用的模型名称。
-   `BASE_URL`: OpenAI 兼容 API 的 Endpoint 地址。
-   `USER_NAME`: 您的 GitHub 用户名。

这些密钥将用于驱动论文筛选和 RSS 生成过程。

推荐使用[火山方舟的批量推理功能](https://www.volcengine.com/docs/82379/1399517)来完成任务。

### 3. 修改配置 (可选)

您可以根据自己的研究兴趣修改 `config.py` 文件：

-   `area_interest_list`: 这是一个列表，您可以添加或修改其中的条目。每个条目包含：
    -   `rss_url`: 您希望订阅的 arXiv RSS feed 地址。您可以从 [arXiv RSS feeds](https://arxiv.org/help/rss) 页面找到不同学科的 RSS 地址。
    -   `area_interest`: 详细描述您的研究兴趣，这将作为提示词 (prompt) 提供给大语言模型 (LLM) 进行论文筛选。描述越具体，筛选结果越精准。
-   `SYSTEM_PROMPT`: 这是提供给 LLM 的系统级提示词，用于指导其行为。通常情况下，您不需要修改此项，除非您希望深度定制 LLM 的筛选逻辑。

### 4. 启用 GitHub Actions

在您 Fork 后的仓库中，进入 "Actions" 标签页。如果看到 "Workflows aren't running on this repository" 的提示，请点击 "Enable Actions on this repository"。

GitHub Actions 将会根据 `.github/workflows/main.yml` 文件中的设定自动运行：

-   **定时运行**: 默认配置为北京时间每周一至周五的 12:01 自动运行。您可以修改 `main.yml` 文件中的 `cron` 表达式来调整运行时间。
-   **手动运行**: 您也可以在 "Actions" 标签页中选择 "Run Arxiv Filter" 工作流，然后点击 "Run workflow" 手动触发。

### 5. 订阅生成的 RSS Feed

工作流成功运行后，会在您的仓库的 `gh-pages` 分支下生成或更新 `feed.xml` 文件。

您可以通过以下链接订阅筛选后的论文：

`https://<YOUR_GITHUB_USERNAME>.github.io/arxiv_filter/feed.xml`

请将 `<YOUR_GITHUB_USERNAME>`替换为您的 GitHub 用户名。

## 工作流程

1.  **检查更新 (`check_updates.py`)**: GitHub Actions 定时触发，首先运行 `check_updates.py` 脚本。该脚本会请求 `config.py` 中定义的 arXiv RSS feed 地址，并与本地缓存的 `rss_cache.json` 文件比较，判断是否有新的论文发布。
2.  **筛选论文 (`run_filter.py`)**: 如果检测到更新，`run_filter.py` 脚本会被执行。它会读取 `rss_cache.json` 中的新论文信息，并利用 `batch_inference.py` 通过配置的 LLM API (例如 OpenAI, VolcEngine Ark API) 根据您在 `config.py` 中定义的 `area_interest` 进行筛选。筛选结果（包括论文标题、链接、作者、摘要以及 LLM 生成的中文简介）会保存在 `arxiv_updates` 目录下的一个以日期命名的 JSON 文件中。
3.  **生成 RSS (`generate_rss.py`)**: `generate_rss.py` 脚本会读取最新的 JSON 结果文件，并生成一个标准的 RSS 文件 (`feed.xml`)。
4.  **部署 RSS (`.github/workflows/main.yml`)**: GitHub Actions 工作流最后会将生成的 `feed.xml` 文件自动部署到您仓库的 `gh-pages` 分支。这样，您就可以通过公开的 URL 访问并订阅这个 RSS feed。

## 许可证

MIT License
