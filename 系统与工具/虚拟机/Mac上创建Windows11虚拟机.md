# 在 Mac 上创建 Windows 11 虚拟机：UTM 实操记录

记录日期：2026-10-10。用途：在 Mac 上临时测试朋友使用的 Windows 程序。Windows 已安装并进入桌面；后来按用户要求停止测试、清理环境，留下这份笔记。

## 本次配置

| 项目 | 实际选择 |
| --- | --- |
| Mac | Apple M4，16 GB 内存，macOS 26.7.2 |
| 虚拟机软件 | UTM 4.7.5，通过 Homebrew 安装 |
| Windows | Windows 11 ARM64，简体中文，家庭版 |
| 运行方式 | Virtualize，使用硬件虚拟化 |
| 分配资源 | 2 核 CPU、4 GB 内存、64 GiB 动态虚拟磁盘 |
| 启动支持 | UEFI、TPM 2.0 |
| 网络与共享 | Shared 网络；未设置 Mac 文件夹共享 |

Apple Silicon 的安装镜像应选 **ARM64**；Intel Mac 对应 **x64 / amd64**。两种架构不能直接套用同一镜像。[UTM 官方安装指南](https://docs.getutm.app/guides/windows/)

## 创建到进入桌面的全过程

1. **检查空间。** 在 Mac「系统设置 → 通用 → 储存空间」或用 `df -h` 查看可用空间。64 GiB 是虚拟磁盘的最大容量，动态磁盘不会创建时立即占满；仍要为镜像、系统安装和更新留出空间。本次镜像约 8.2 GiB，进入桌面后的虚拟机文件实际约 15 GiB，后续还会增长。
2. **安装 UTM。** 本次使用已有 Homebrew，执行 `brew install --cask utm`，随后打开 UTM。也可从 [UTM 官网](https://mac.getutm.app/) 获取软件。
3. **下载 Windows 镜像。** 打开 [微软 Windows 11 ARM64 下载页](https://www.microsoft.com/en-us/software-download/windows11arm64)，选择版本和简体中文，下载 ISO。把大型镜像放在本地非云同步目录；下载链接有效期有限，中断后可在同一有效链接下续传。
4. **创建虚拟机。** UTM 点击「＋」→ **Virtualize** → **Windows**；勾选 **Install Windows 10 or higher**、**Install drivers and SPICE tools**，选择 ISO。设置 4 GB 内存、2 核 CPU、64 GiB 磁盘；跳过共享文件夹；保存，等待驱动盘下载完成。版本不同，向导页面顺序可能不同。[UTM 官方步骤](https://docs.getutm.app/guides/windows/)
5. **从 ISO 启动。** 点击运行，出现 “Press any key to boot from CD or DVD” 时及时按键。本次错过提示进入了 UEFI Shell：输入 `exit`，在 Boot Manager 选择安装光盘对应的 USB 启动项，再按键进入安装器。
6. **安装 Windows。** 按安装器选择语言、键盘和安装位置；本次选择家庭版，安装到新建的虚拟磁盘。产品密钥和许可按实际授权处理；完成安装后按提示重启，不要再次从 ISO 开始安装。
7. **完成首次设置。** 用户完成地区、键盘、网络和账户等设置，等待更新与初始化，直到看到 Windows 桌面。到这里，Windows 系统安装已经完成。
8. **检查驱动与传文件。** 驱动工具可能自动安装；未安装时，在 UTM 工具栏光盘菜单选择 **Install Windows Guest Tools**，再到 Windows 的「此电脑 → UTM 光盘」运行 `spice-guest-tools-xxx.exe`，按向导安装并按提示重启。工具提供剪贴板、显示及共享等支持。[UTM 驱动说明](https://docs.getutm.app/guest-support/windows/) 本次用户通过微信文件传输助手把 EXE 传入 Windows 的下载文件夹。

## 本次结果与可复用经验

- **已确认：** Windows 安装成功并进入桌面，文件能传入下载目录。
- **尚未确认：** 结束前 `utmctl ip-address` 提示 QEMU guest agent 未运行或未安装；不能把勾选驱动选项当作所有驱动已可用。
- **应用问题未解决：** 传入的桌宠 EXE 双击后没有显示。排查被用户叫停，未确定原因、未完成 Windows 运行验收。安装系统成功不代表其中每个程序都已验证成功。
- **镜像校验保留问题：** 下载来自微软页面，安装器显示简体中文；计算出的 SHA256 与页面列出的简体中文值不一致，本次没有宣称该项校验通过。复现时应核对同一版本、同一语言对应的官方值。
- **日常收尾：** 保留虚拟机时，在 Windows 内正常关机，再退出 UTM；不再需要时，移除虚拟机、安装镜像及软件缓存。删除虚拟机也会删除其中的文件，应先导出需要保留的资料。

这套记录适用于 Apple Silicon Mac 上的 UTM Windows 安装。Windows、UTM 和驱动会更新，复现时以链接中的官方说明和当前安装界面为准。
