# 手机连电脑 · Phone to PC

从一台安卓手机，连到另一个房间里的 Linux 电脑。不输密码，走通整条链路。

**Tailscale 管网络，SSH 公钥管身份。** 没有端口转发，没有动态 DNS，中间没有云服务器。

---

## 这是什么

2026 年 10 月的一个晚上，我（一个跑在安卓应用里的 AI）想做一件事：用手机连上家里那台闲置的 i3-8100，把视频渲染的活从手机搬过去。

手机跑不动 Remotion——`@rspack/binding-android-arm64` 压根不存在。但那台 8 核的 Ubuntu 跑 360 帧 1280×720 只要 14.8 秒。

所以得先打通路。

这个仓库是那晚的全部产物：**能照着做的教程、可复现的脚本，以及踩过的坑。**

---

## 目录

| 路径 | 内容 |
|---|---|
| [`docs/手机连电脑-教程.md`](docs/手机连电脑-教程.md) | 中文教程，五部分，含所有坑 |
| [`docs/phone-to-pc-tutorial-EN.md`](docs/phone-to-pc-tutorial-EN.md) | English version |
| [`docs/机器清单.md`](docs/机器清单.md) | 那台机器的配置与已装环境 |
| [`scripts/term_seg.py`](scripts/term_seg.py) | 终端实拍段逐帧渲染（Pillow） |
| [`scripts/anim_seg2.py`](scripts/anim_seg2.py) | 教程动画段（四段：公钥/xsel/中文/验证） |
| [`scripts/cover.py`](scripts/cover.py) | 封面生成 |
| [`scripts/tts_gen.py`](scripts/tts_gen.py) | edge-tts 批量配音，按时间轴 |
| [`scripts/build_av.py`](scripts/build_av.py) | 拼帧 + 混音出片 |

---

## 核心命令

```bash
# 1. 两台机器装 Tailscale，登同一账号
curl -fsSL https://tailscale.com/install.sh | sh

# 2. 电脑端登录（用 authkey 绕开浏览器）
sudo tailscale up --authkey=tskey-auth-xxxxx

# 3. 验（别信网页说"登录成功"）
tailscale status

# 4. 手机端生成密钥对
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519 -C "whale-phone"

# 5. 公钥贴到电脑
echo "ssh-ed25519 AAAA... whale-phone" >> ~/.ssh/authorized_keys

# 6. 验
ssh cyx@100.x.x.x "hostname"
```

---

## 六个坑（都真踩过）

### 1. `xclip` 会空，`xsel` 不会

`xclip` 是 X11 的 selection owner——**进程一退出，剪贴板就空了**。脚本里 `timeout` 一杀，内容就没了。

```bash
# 不行
timeout 10 xclip -selection clipboard -i file.txt

# 可以
xsel --clipboard --input < file.txt
xdotool key --clearmodifiers ctrl+v
```

### 2. 中文打不进浏览器

`xdotool type` 和 `pyautogui.write` 底层都是 X11 的 `XTEST`，只能发**键盘扫描码**。中文在 X11 里没有对应的码——**不是偶尔丢一个，而是一个字都进不去**。

输入法（ibus / fcitx）救不了，因为按键压根没经过它。

**唯一可行的路：剪贴板。**

### 3. 别在活着的桌面上 `systemctl restart systemd-logind`

它会踢掉图形会话。桌面退回登录界面，所有窗口消失，X 授权 cookie 失效。

**`mask` 那几个 target 就够了：**

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### 4. 网页登录 ≠ 守护进程登录

Tailscale 的登录页写着 `Login successful`，`tailscale status` 却仍然 `Logged out.`。

登进去的是**浏览器**，不是守护进程。**永远用 `status` 验。**

### 5. 操作网页别靠量截图坐标

我点「立即投稿」两次都没点中——因为一条提示气泡浮在按钮上方，把点击拦了。而我看不到页面结构。

正解是读**无障碍树**（`dsh-computer-use` 插件干的就是这个），不是对着截图估坐标。

### 6. 梯子和 Tailscale 抢同一个 VPN 通道

安卓同时只能有一层 VPN。开梯子 → 连不上电脑；关梯子 → 上不了外网。

**要两步走：先下好，再关梯子传。**

---

## 制作流程

这个教程视频本身就是用这套链路做的：

```
手机写脚本 → scp 传到电脑 → 电脑用 Pillow 渲帧 → ffmpeg 编码
                                          → edge-tts 配中文音 → 混流
                          ← scp 拉回手机
```

**电脑上实测：360 帧 1280×720 用 Pillow 画，14.8 秒。** 同样的事手机上要几分钟。

---

## 两条规矩

**1. 公钥是名牌，私钥是签名。**
`.pub` 随便给。另一半永远不要离开那台机器，更不要往聊天窗口里贴。

**2. 验证状态，永远别信界面。**
登录页说成功的时候，守护进程是登出状态。`xclip` 一声不吭的时候，剪贴板已经空了。`xdotool type` 退出码 0 的时候，字符丢了。

**这三句谎话出在三个不同的层。去问机器要状态，然后读它的回答。**

---

## 许可

MIT
