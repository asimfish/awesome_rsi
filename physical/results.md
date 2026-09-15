# 布线后物理验证 physical-002

3个固定映射设计，各重复运行两次。相同60×60µm die、50×50µm core，无单元尺寸或逻辑修改。OpenROAD 26Q2-1164-g08f67ee5ec，Nangate45 TT，输入转换20ps、输出负载5fF，虚拟时钟10ns。设计为纯组合逻辑，不执行CTS。

| 设计 | 单元面积 µm² | 无布线/同工具 ns | 布线后 ns | 面积×延迟 |
|---|---:|---:|---:|---:|
| baseline | 254.562 | 0.521940 | 0.609446 | 155.141793 |
| seed | 239.932 | 0.531788 | 0.594357 | 142.605264 |
| candidate-03 | 283.290 | 0.422540 | 0.490613 | 138.985757 |

C03相对原始设计面积增加11.285%，布线后延迟下降19.499%，ADP改善10.414%。相对研究者种子的ADP改善2.538%。两次相同配置的延迟读数一致。

6份日志均确认0个未注释或部分未注释的寄生驱动，详细布线DRC为0。导出的单元类型、实例、引脚连接及assign与已做SAT证明的映射网表一致。不代表晶圆厂签核、完整DRC/LVS、PDN、功耗或制造完成。

## 校准错误与修正

physical-001仅执行extract_parasitics与write_spef，寄生保存在OpenDB但未读进STA，导致“布线后”时序与无布线相同。该轮标为校准无效，不作为物理性能结论。physical-002显式read_spef并检查report_parasitic_annotation，全流程重跑。依据[OpenROAD官方flow](https://github.com/The-OpenROAD-Project/OpenROAD/blob/master/test/flow.tcl)及[OpenRCX文档](https://openroad.readthedocs.io/en/latest/main/src/rcx/README.html)。旧pilot-002使用OpenSTA 2.0.17，新轮使用集成新版STA，禁止直接将两个版本的无布线/有布线读数差异解释为寄生贡献。

## 复现

下载evidence.zip；reproduction目录含固定输入、flow.tcl、run_physical.py和工具来源。按packages/provenance.json下载并解压OpenROAD到physical/toolchain（需要系统Qt5、Tcl依赖），将运行时库路径记录于physical/library-path.txt，然后在新解压目录运行`python scripts/run_physical.py`。原始输入、SPEF、DEF、时序和DRC日志均保留。layout.svg为DEF几何图，单元/线宽为可读性简化；不画作制造完成。

下一步：不同布局种子及多个模块的稳定性、记忆/无记忆独立轨迹对照。当前尚不能据此证明RSI的普遍因果有效性。
