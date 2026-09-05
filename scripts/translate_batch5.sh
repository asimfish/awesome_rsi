#!/bin/bash
# 第五批中译：补齐 34 篇尚无中文版的英文 PDF + 3 篇有文本层的起源经典
# 用法: scripts/translate_batch5.sh A|B|C   （三条队列可并行）
#   A = 有专门解读报告的前沿论文（优先）
#   B = 桥接 / 宏观 / 自动研究谱系
#   C = 起源经典（Good 1965 为扫描件无文本层，跳过）
set -u
export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/usr/local/bin
set -a; source ~/Desktop/research/paper_china/.env; set +a
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ST=~/Code/super_translate
CACHE=/tmp/rsi_translate_cache; mkdir -p "$CACHE"
Q="${1:?queue A|B|C}"

case "$Q" in
A) SRC="$REPO/papers/en"; DST="$REPO/papers/zh"; QUEUE=(
  2606.05922_RHO 2606.06324_HarnessFix 2607.13070_FalsifiableReleaseGates 2608.08471_SESG
  2608.09380_OpenLoopEvolve 2608.22103_HVTB 2608.07449_SkillProx 2608.12720_ERSkill
  2608.15071_EvoHarness 2608.15165_SkillCommit 2608.16114_HyperSkill 2608.08466_HSI
  2606.04507_SCORE 2605.30621_HarnessUpdatingNotBenefit 2603.19461_Hyperagents );;
B) SRC="$REPO/papers/en"; DST="$REPO/papers/zh"; QUEUE=(
  2507.19457_GEPA 2408.08435_ADAS 2410.10762_AFlow 2506.13131_AlphaEvolve 2509.19349_ShinkaEvolve
  2305.16291_Voyager 2408.06292_AIScientist 2605.24539_DemoEvolve 2605.26340_ScientistOne 2605.27276_SIA
  2606.01770_AdaptiveAutoHarness 2606.25996_Autodata 2602.08234_SkillRL 2605.10663_EvolvingRL
  2512.23760_ASG-SI 2602.01750_ARA 2601.03315_WhyLLMsArentScientistsYet 2503.14499_METR_LongTasks
  2309.11690_ExplosiveGrowthReview );;
C) SRC="$REPO/papers/classics"; DST="$REPO/papers/classics"; QUEUE=(
  2008_Omohundro_BasicAIDrives 2010_Chalmers_Singularity 2013_Yudkowsky_IEM );;
*) echo "unknown queue $Q"; exit 1;;
esac

cd "$ST"
for name in "${QUEUE[@]}"; do
  src="$SRC/${name}.pdf"; dst="$DST/${name}_zh.pdf"
  [ -f "$src" ] || { echo "[missing-src] $name"; continue; }
  [ -f "$dst" ] && { echo "[skip] $name"; continue; }
  echo "=== [$(date +%H:%M:%S)] Q$Q translating $name ==="
  uv run python -m pdf_zh_translator translate "$src" "$dst" \
    --api-mode deepseek --api-key-env PAPER_CHINA_DEEPSEEK_API_KEY \
    --preserve-graphics-text --cache-file "$CACHE/${name}.translation-cache.jsonl" \
    || echo "[FAIL] $name"
  echo "=== [$(date +%H:%M:%S)] Q$Q done $name ==="
done
echo "QUEUE_${Q}_ALL_DONE"
