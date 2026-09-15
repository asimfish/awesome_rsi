# 服务器资源监控

公开面板：https://asimfish.github.io/awesome_rsi/scenes.html#server
数据：https://raw.githubusercontent.com/asimfish/awesome_rsi/server-data/servers.json

服务器每 5 分钟采集一次，浏览器每 60 秒读取；GitHub 缓存还可能增加延迟。15 分钟没有采样即显示过期，读不到新记录显示同步失败。备用 JSON 是部署时快照，显示“备用快照”及真实时间。历史仅保存最近 36 次采样，不生成过去的数据。

采集内容：CPU 1 秒利用率、逻辑核和 load；内存与 Swap；系统盘和实验存储容量；每张 NVIDIA GPU 的显存、利用率、温度、功耗；本项目工作进程与实验状态。

资源属于整机共享资源。GPU 计算进程按是否属于本项目控制器/EDA 进程及其后代区分。其他项目只显示数量，不展示其命令、名称、PID 或用户。未识别计算进程不代表显存空闲（可能有图形进程）。无法读取指标时显示不可用，不用零替代。

公开 JSON 由固定字段构造，不含主机名、IP、GPU UUID、PID、用户名、命令行、环境变量或凭据。

## 服务管理

用户级 systemd timer：silicon-loop-server.timer；单次采集服务：silicon-loop-server.service。本服务器用户已启用 Linger，登出和对话结束不会停掉定时器；启动用户管理器后 45 秒首次触发，其后每 5 分钟。失败后下一周期重试，超过 100 秒结束单次采集；文件锁防止重叠。

```bash
systemctl --user status silicon-loop-server.timer
systemctl --user start silicon-loop-server.service  # 手动采集并公开上传一次
systemctl --user disable --now silicon-loop-server.timer  # 停止后续自动采集
journalctl --user -u silicon-loop-server.service -n 10
```

如果当前 shell 没有会话总线环境，设 XDG_RUNTIME_DIR 为 /run/user/<你的UID>，DBUS_SESSION_BUS_ADDRESS 为 unix:path=/run/user/<你的UID>/bus。

部署新服务器时修改两个 unit 的工作目录与 ExecStart 路径。依赖 Python 标准库、Linux /proc、可选 nvidia-smi，以及用户已配置的 GitHub git credential helper。密钥只在上传进程内存中使用，不写到 unit/数据/日志中。

server-data 是独立数据分支，上传仅修改 servers.json，不触发 gh-pages 网页重建，也不覆盖实验状态文件。数据上传失败会保留本地采样、公开页面按时间判过期。定时器没有权限接收网页命令或启动模型实验。

验证：GPU 不可用/读数未知、计算进程归属和公开字段白名单有单元测试；浏览器测试覆盖真实读数、共享资源区分、过期/网络失败、GPU 不可用、390/768/1440 px 布局。
