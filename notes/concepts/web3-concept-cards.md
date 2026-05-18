# Web3 基础概念卡片 · Week 1

> 八张卡片,从「钱包」走到「测试网」。每张控制 250 字左右,讲程序员能立刻用的细节。
> 锚点优先 Ethereum.org / EIP / 官方协议文档。

---

## 卡片 1 — 钱包 (Wallet)

**一句话定义**:管理密钥、发起签名与广播交易的工具,本身不存储资产。

**核心机制**:
钱包是密钥管理与签名前端,资产实际记录在链上账户余额中。EOA 钱包客户端 (如 MetaMask、Rabby) 在本地保管私钥,签名后通过 RPC 节点广播交易。智能合约钱包 (Smart Contract Wallet, SCW,如 Safe、Argent) 把"账户"实现成一份链上合约,签名/校验/恢复逻辑都写在合约里,客户端 (App、SDK) 只是它的操作面板。

**能做什么 / 不能做什么**:
- 能:生成与导入密钥、签名消息与交易、连接 dApp (WalletConnect / EIP-1193)
- 能:为 SCW 提供 UI、模拟交易、估算 gas
- 不能:替你保管资产 (资产在链上,不在钱包里)
- 不能:撤销已上链的交易、找回未备份的助记词

**常见误区**:把"钱包 App"和"账户"混为一谈——卸载 App 不等于丢币,只要助记词在,账户就在。

**官方文档锚点**:https://ethereum.org/en/wallets/

---

## 卡片 2 — 账户 (Account)

**一句话定义**:链上由地址寻址、持有余额与 nonce 的状态对象。

**核心机制**:
以太坊有两种账户:外部拥有账户 (Externally Owned Account, EOA) 由私钥控制,只有 `balance`、`nonce`,不能存代码;合约账户 (Contract Account) 由部署时的字节码控制,拥有 `balance`、`nonce`、`code`、`storage`,行为完全由合约逻辑决定。所有交易必须由 EOA 发起 (ERC-4337 之前),合约账户被动响应调用。EIP-7702 之后,EOA 也可以临时挂载合约代码。

**能做什么 / 不能做什么**:
- EOA 能:直接付 gas、签交易、控制 SCW
- 合约账户能:自定义鉴权、批量调用、社交恢复
- EOA 不能:自定义签名规则、限额、多签
- 合约账户不能:在 ERC-4337 之前主动发起 L1 交易

**常见误区**:认为"地址 = 钱包",其实地址只是账户的标识符。

**官方文档锚点**:https://ethereum.org/en/developers/docs/accounts/

---

## 卡片 3 — 助记词 / 私钥 / 地址

**一句话定义**:助记词派生私钥,私钥派生公钥与地址,这是单向链路。

**核心机制**:
助记词 (Mnemonic / Seed Phrase, BIP-39) 是 12 或 24 个单词的种子,经 PBKDF2 推出 512-bit seed;再由 BIP-32/BIP-44 通过分层确定性 (HD) 派生路径生成多个私钥;私钥 (Private Key, 256-bit) 经 secp256k1 椭圆曲线得到公钥;公钥取 keccak256 哈希后的最后 20 字节就是地址 (Address)。整条链路单向:有助记词可推出全部,反过来不行。

**能做什么 / 不能做什么**:
- 能:用一份助记词在不同钱包间恢复全部地址
- 能:私钥离线签名后再广播 (冷签)
- 不能:从地址反推私钥或助记词
- 不能:更改助记词对应的私钥 (只能新建)

**常见误区**:把助记词截图存相册或云盘——任何同步到服务器的备份都等于把钱发上网。

**官方文档锚点**:https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki

---

## 卡片 4 — 签名 (Signature)

**一句话定义**:用私钥对消息哈希做 ECDSA 运算,产生可被公钥验证的凭证。

**核心机制**:
EVM 链上有两类签名。Transaction Signature 对交易体 (RLP 编码) 做哈希后签名,结果作为交易的 `v, r, s` 字段广播上链,会改变状态、消耗 gas。Message Signature 不上链,常见结构化方案有 `personal_sign` (EIP-191) 和 `eth_signTypedData_v4` (EIP-712),用于登录认证 (Sign-In with Ethereum, SIWE)、订单、授权 (Permit, EIP-2612) 等场景。智能账户用 `isValidSignature` (EIP-1271) 验证签名。

**能做什么 / 不能做什么**:
- 能:链下证明身份、链下授权、链上发交易
- 能:做 gasless 操作 (签名后由 relayer 代付)
- 不能:签名等于"安全",钓鱼签名同样能掏空账户
- 不能:撤销已签发的 Permit (除非合约提供 nonce 失效)

**常见误区**:把"签消息"当作零风险——盲签 (blind signing) 是最大攻击面。

**官方文档锚点**:https://eips.ethereum.org/EIPS/eip-712

---

## 卡片 5 — 交易 (Transaction)

**一句话定义**:由 EOA 签发、改变链上状态的最小执行单元。

**核心机制**:
交易包含 `nonce`、`to`、`value`、`data`、`gasLimit`、`maxFeePerGas` / `maxPriorityFeePerGas` (EIP-1559)、`chainId` (EIP-155) 与签名。生命周期:钱包构造 → 私钥签名 → 通过 RPC 提交进入 mempool → 矿工/验证者打包 → 区块确认 → 最终性 (finality)。`to` 为空表示部署合约,带 `data` 表示调用合约方法 (ABI 编码的 calldata)。失败的交易也消耗 gas。

**能做什么 / 不能做什么**:
- 能:转账、部署/调用合约、批量操作 (multicall)
- 能:用 `speed up` (相同 nonce 高 gas) 替换 pending 交易
- 不能:回滚已确认交易 (只能再发反向交易)
- 不能:跳过 nonce 顺序执行

**常见误区**:以为"交易失败 = 不扣钱"——其实 gas 照扣,只是状态回滚。

**官方文档锚点**:https://ethereum.org/en/developers/docs/transactions/

---

## 卡片 6 — Gas

**一句话定义**:执行 EVM 操作的计量单位,用 ETH 支付以防止滥用。

**核心机制**:
每个 opcode 都有 gas 成本,交易总消耗 = `gasUsed × effectiveGasPrice`。EIP-1559 把价格拆成 `baseFee` (按区块拥堵自动调整,被销毁) 和 `priorityFee` (给验证者的小费)。L1 (Ethereum Mainnet) gas 单价高、波动大;L2 (Optimism、Arbitrum、Base) 把交易压缩后批量发到 L1,gas 主要由 L1 calldata 成本 + L2 执行成本组成,通常比 L1 便宜 10–100 倍。EIP-4844 (blob) 进一步降低 L2 DA (Data Availability) 成本。

**能做什么 / 不能做什么**:
- 能:用 `gasLimit` 设置上限保护、用 `maxFeePerGas` 控成本
- 能:在 L2 上做高频小额操作 (社交、游戏)
- 不能:把 gas 设为 0 提交交易
- 不能:让用户"无感知"——除非用 Paymaster 代付

**常见误区**:把 L2 gas 直接换算成 L1,实际两者结构完全不同。

**官方文档锚点**:https://ethereum.org/en/developers/docs/gas/

---

## 卡片 7 — 智能合约 (Smart Contract)

**一句话定义**:部署到链上、按确定性规则自动执行的不可变代码。

**核心机制**:
合约用 Solidity / Vyper 编写,编译成 EVM 字节码后通过部署交易写入链上,获得唯一地址。每次被调用时,EVM 在所有节点上重新执行相同字节码,得到一致状态变更——这就是"无需信任"的来源。状态保存在合约 storage 槽位,只能通过合约方法修改。代码默认不可升级 (immutable),升级需走代理模式 (Proxy, EIP-1967) 或 Diamond (EIP-2535)。

**能做什么 / 不能做什么**:
- 能:执行确定性逻辑、托管资产、组合调用 (composability)
- 能:公开可审计、任何客户端可读
- 不能:主动访问外部数据 (需 oracle 如 Chainlink)
- 不能:像后端那样热更新——bug 上线即资产风险

**与"普通后端"差异**:后端可以重启、回滚、加日志、灰度发布;合约一旦部署,bug 通常意味着真金白银损失,所以必须先测试、审计、形式化验证。

**常见误区**:认为"开源就安全"——开源只是审计前提,不等于审计结果。

**官方文档锚点**:https://docs.soliditylang.org/

---

## 卡片 8 — 测试网 (Testnet)

**一句话定义**:与主网同协议但使用免费代币的独立网络,用于开发与验证。

**核心机制**:
测试网 (Testnet) 与主网 (Mainnet) 共享相同的 EVM 与协议规则,但 chainId 不同、代币没有真实价值。Sepolia (chainId 11155111) 是当前以太坊推荐的应用层测试网,由小型验证者集维护;Holesky (chainId 17000) 主要用于验证者与质押测试。开发者通过水龙头 (Faucet) 领取 SepoliaETH,部署同一份合约字节码,行为与主网一致。常见区块浏览器 Etherscan、Blockscout 都提供测试网入口。

**能做什么 / 不能做什么**:
- 能:零成本部署、调用、调试合约
- 能:在前端连接钱包做端到端联调
- 不能:在测试网上的"安全"等同于主网安全 (MEV、流动性、攻击者动机都不同)
- 不能:把测试币兑换成真实资产

**常见误区**:把"测试网跑通"当作"主网可上线"——主网还要考虑 MEV、gas 突变、合约升级权限治理。

**官方文档锚点**:https://ethereum.org/en/developers/docs/networks/#ethereum-testnets
