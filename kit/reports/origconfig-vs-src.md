# 内核 config 与源码一致性核对

- 内核树: `/root/.codebuddy/artifact/2f8a7d30-9c21-4f0b-1d67-ab66cccb4000/build2`
- 启用项: 1811（y/m）
- 缺失源码: **0**
- 未接线: 759
- config 残留: 6

## 一、config 开了但源码缺失

无。

## 二、Kconfig 有定义但 Makefile 未接线

| CONFIG | 类型 | Kconfig | 说明 |
|---|---|---|---|
| `CONFIG_64BIT` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_ADVISE_SYSCALLS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_AIO` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_ALLOW_DEV_COREDUMP` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_ANDROID_PARANOID_NETWORK` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_CLOCKSOURCE_DATA` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_DMA_ADDR_T_64BIT` | y | kernel/dma/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_ENABLE_MEMORY_HOTPLUG` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_ENABLE_MEMORY_HOTREMOVE` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_FLATMEM_ENABLE` | y | arch/arc/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_CACHE_LINE_SIZE` | y | arch/arc/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_DEBUG_VIRTUAL` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_ARCH_HAS_DEVMEM_IS_ALLOWED` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_ARCH_HAS_ELF_RANDOMIZE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_FAST_MULTIPLIER` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_FORTIFY_SOURCE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_GCOV_PROFILE_ALL` | y | kernel/gcov/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_GIGANTIC_PAGE` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_HOLES_MEMORYMODEL` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_KCOV` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_ARCH_HAS_MEMBARRIER_SYNC_CORE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_PTE_SPECIAL` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_RELR` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_SET_MEMORY` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_SG_CHAIN` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_STRICT_KERNEL_RWX` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_STRICT_MODULE_RWX` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_SYSCALL_WRAPPER` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_TICK_BROADCAST` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HAS_UBSAN_SANITIZE_ALL` | y | lib/Kconfig.ubsan | 整条链无引用 |
| `CONFIG_ARCH_HAVE_NMI_SAFE_CMPXCHG` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_HIBERNATION_POSSIBLE` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_KONA` | y | arch/arm64/Kconfig.platforms | 整条链无引用 |
| `CONFIG_ARCH_MEMORY_PROBE` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_PROC_KCORE_TEXT` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_QCOM` | y | arch/arm/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_ARCH_SELECT_MEMORY_MODEL` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SPARSEMEM_DEFAULT` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SPARSEMEM_ENABLE` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_ATOMIC_RMW` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_DEBUG_PAGEALLOC` | y | arch/arm/Kconfig.debug | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_INT128` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_LTO_CLANG` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_MEMORY_FAILURE` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_NUMA_BALANCING` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_SHADOW_CALL_STACK` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_SPECULATIVE_PAGE_FAULT` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_THINLTO` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUPPORTS_UPROBES` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_SUSPEND_POSSIBLE` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_USE_CMPXCHG_LOCKREF` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_USE_QUEUED_RWLOCKS` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_ARCH_USE_QUEUED_SPINLOCKS` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_ARCH_WANT_COMPAT_IPC_PARSE_VERSION` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_ARCH_WANT_FRAME_POINTERS` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_ARCH_WANT_HUGE_PMD_SHARE` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64` | y | arch/arm64/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_ARM64_4K_PAGES` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_CRYPTO` | y | arch/arm64/crypto/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_DMA_USE_IOMMU` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_1024718` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_1188873` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_1463225` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_1542418` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_1542419` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_819472` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_824069` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_826319` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_827319` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_832075` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_843419` | y | arch/arm64/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_ARM64_ERRATUM_845719` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_ERRATUM_858921` | y | drivers/clocksource/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_HW_AFDBM` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_LSE_ATOMICS` | y | arch/arm64/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_ARM64_MODULE_PLTS` | y | arch/arm64/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_ARM64_PAN` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_PA_BITS_48` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_RAS_EXTN` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_SSBD` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_SVE` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_SW_TTBR0_PAN` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_TAGGED_ADDR_ABI` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_UAO` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM64_VA_BITS_39` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARMV8_DEPRECATED` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_ARM_ARCH_TIMER_EVTSTREAM` | y | drivers/clocksource/Kconfig | 整条链无引用 |
| `CONFIG_ARM_ARCH_TIMER_OOL_WORKAROUND` | y | drivers/clocksource/Kconfig | 整条链无引用 |
| `CONFIG_ASN1` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_AUDIT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_AUDITSYSCALL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_AUDIT_ARCH_COMPAT_GENERIC` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_AUDIT_TREE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_AUDIT_WATCH` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BACKLIGHT_LCD_SUPPORT` | y | drivers/video/backlight/Kconfig | 整条链无引用 |
| `CONFIG_BALANCE_ANON_FILE_RECLAIM` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_BASE_FULL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BCMA_POSSIBLE` | y | drivers/bcma/Kconfig | 整条链无引用 |
| `CONFIG_BFQ_GROUP_IOSCHED` | y | block/Kconfig.iosched | 整条链无引用 |
| `CONFIG_BINARY_PRINTF` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_BLK_CGROUP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BLK_DEV` | y | drivers/block/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_BLOCK` | y | block/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_BPF` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BPF_JIT` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_BPF_JIT_ALWAYS_ON` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BPF_SYSCALL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BQL` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_BRANCH_PROFILE_NONE` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_BRIDGE_IGMP_SNOOPING` | y | net/bridge/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_BT_BREDR` | y | net/bluetooth/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_BT_HS` | y | net/bluetooth/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_BT_LE` | y | net/bluetooth/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_BUG` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BUILDTIME_EXTABLE_SORT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BUILD_ARM64_UNCOMPRESSED_KERNEL` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_BUILD_BIN2C` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_BUS_AUTO_SUSPEND` | y | drivers/net/wireless/cnss2/Kconfig | 整条链无引用 |
| `CONFIG_CAN_CALC_BITTIMING` | y | drivers/net/can/Kconfig | 整条链无引用 |
| `CONFIG_CAN_DEV` | y | drivers/net/can/Kconfig | 整条链无引用 |
| `CONFIG_CAVIUM_ERRATUM_22375` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_CAVIUM_ERRATUM_23154` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_CAVIUM_ERRATUM_27456` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_CAVIUM_ERRATUM_30115` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_CAVIUM_PTP` | y | drivers/net/ethernet/cavium/Kconfig | 整条链无引用 |
| `CONFIG_CC_HAS_ASM_GOTO` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CC_HAS_AUTO_VAR_INIT_PATTERN` | y | security/Kconfig.hardening | 整条链无引用 |
| `CONFIG_CC_HAS_AUTO_VAR_INIT_ZERO` | y | security/Kconfig.hardening | 整条链无引用 |
| `CONFIG_CC_HAS_KASAN_GENERIC` | y | lib/Kconfig.kasan | 整条链无引用 |
| `CONFIG_CC_HAS_KASAN_SW_TAGS` | y | lib/Kconfig.kasan | 整条链无引用 |
| `CONFIG_CC_HAS_SANCOV_TRACE_PC` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_CC_HAS_STACKPROTECTOR_NONE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_CC_HAVE_SHADOW_CALL_STACK` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_CC_IS_CLANG` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CC_OPTIMIZE_FOR_PERFORMANCE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CFG80211_CRDA_SUPPORT` | y | net/wireless/Kconfig | 整条链无引用 |
| `CONFIG_CFG80211_DEFAULT_PS` | y | net/wireless/Kconfig | 整条链无引用 |
| `CONFIG_CFG80211_INTERNAL_REGDB` | y | net/wireless/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CFG80211_REQUIRE_SIGNED_REGDB` | y | net/wireless/Kconfig | 整条链无引用 |
| `CONFIG_CFG80211_USE_KERNEL_REGDB_KEYS` | y | net/wireless/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CFQ_GROUP_IOSCHED` | y | block/Kconfig.iosched | 整条链无引用 |
| `CONFIG_CGROUPS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CGROUP_BPF` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CGROUP_CPUACCT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CGROUP_FREEZER` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CGROUP_SCHED` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CGROUP_WRITEBACK` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CLD_LL_CORE` | y | drivers/net/wireless/Kconfig | 整条链无引用 |
| `CONFIG_CLONE_BACKWARDS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_CLS_U32_MARK` | y | net/sched/Kconfig | 整条链无引用 |
| `CONFIG_CLZ_TAB` | y | lib/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CMA_SIZE_SEL_MBYTES` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_CMDLINE_EXTEND` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_CNSS2_QMI` | y | drivers/net/wireless/cnss2/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CNSS_ASYNC` | y | drivers/net/wireless/cnss2/Kconfig | 整条链无引用 |
| `CONFIG_COMPACTION` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_COMPAT` | y | arch/arm64/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_COMPAT_32BIT_TIME` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_COMPAT_NETLINK_MESSAGES` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_COMPAT_OLD_SIGACTION` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_CONSOLE_TRANSLATIONS` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_CORESIGHT_CTI_SAVE_DISABLE` | y | drivers/hwtracing/coresight/Kconfig | 整条链无引用 |
| `CONFIG_CP15_BARRIER_EMULATION` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_CPUSETS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE` | y | drivers/cpufreq/Kconfig | 整条链无引用 |
| `CONFIG_CPU_FREQ_GOV_SCHEDUTIL` | y | drivers/cpufreq/Kconfig | 整条链无引用 |
| `CONFIG_CPU_IDLE_GOV_MENU` | y | drivers/cpuidle/Kconfig | 整条链无引用 |
| `CONFIG_CPU_IDLE_MULTIPLE_DRIVERS` | y | drivers/cpuidle/Kconfig | 整条链无引用 |
| `CONFIG_CPU_ISOLATION` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CPU_PM` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_CPU_THERMAL` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRC32_SLICEBY8` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_CROSS_MEMORY_ATTACH` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_AEAD` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_AKCIPHER` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_ALGAPI` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_BLKCIPHER` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_DEV_QCEDEV` | y | drivers/crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_DEV_QCOM_ICE` | y | drivers/crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_DEV_QCRYPTO` | y | drivers/crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_DRBG_HMAC` | y | crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_DRBG_MENU` | y | crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_HASH` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_HW` | y | drivers/crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_KPP` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_MANAGER` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_MANAGER_DISABLE_TESTS` | y | crypto/Kconfig | 整条链无引用 |
| `CONFIG_CRYPTO_NULL` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_RNG` | y | crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_CRYPTO_RNG_DEFAULT` | y | crypto/Kconfig | 整条链无引用 |
| `CONFIG_DCACHE_WORD_ACCESS` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_DEBUG_ALIGN_RODATA` | y | arch/arm/mm/Kconfig | 整条链无引用 |
| `CONFIG_DEBUG_BUGVERBOSE` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_DEBUG_INFO` | y | lib/Kconfig.debug | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DEBUG_KERNEL` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_DECOMPRESS_BZIP2` | y | lib/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DECOMPRESS_GZIP` | y | lib/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DECOMPRESS_LZ4` | y | lib/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DECOMPRESS_LZMA` | y | lib/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DEFAULT_CFQ` | y | block/Kconfig.iosched | 整条链无引用 |
| `CONFIG_DEFAULT_SECURITY_SELINUX` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_DEVFREQ_THERMAL` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DIAG_OVER_USB` | y | drivers/char/diag/Kconfig | 整条链无引用 |
| `CONFIG_DMA_CMA` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_DMA_SHARED_BUFFER` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_DM_UEVENT` | y | drivers/md/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DM_VERITY_FEC` | y | drivers/md/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DRM_BRIDGE` | y | drivers/gpu/drm/bridge/Kconfig | 整条链无引用 |
| `CONFIG_DRM_PANEL` | y | drivers/gpu/drm/panel/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DRM_PANEL_BRIDGE` | y | drivers/gpu/drm/bridge/Kconfig | 整条链无引用 |
| `CONFIG_DST_CACHE` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_DTC` | y | drivers/of/Kconfig | 整条链无引用 |
| `CONFIG_DUMMY_CONSOLE` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_DVB_MPQ_SW` | y | drivers/media/platform/msm/dvb/demux/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_DVB_NET` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_ECRYPT_FS_MESSAGING` | y | fs/ecryptfs/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_EDAC_KRYO_ARM64_PANIC_ON_UE` | y | drivers/edac/Kconfig | 整条链无引用 |
| `CONFIG_EDAC_LEGACY_SYSFS` | y | drivers/edac/Kconfig | 整条链无引用 |
| `CONFIG_EDAC_SUPPORT` | y | drivers/edac/Kconfig | 整条链无引用 |
| `CONFIG_ELFCORE` | y | fs/Kconfig.binfmt | 整条链无引用 |
| `CONFIG_ELF_CORE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_EMBEDDED` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_ENABLE_MUST_CHECK` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_EPOLL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_EVENTFD` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_EXFAT_DISCARD` | y | fs/exfat/Kconfig | 整条链无引用 |
| `CONFIG_EXPERT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_EXT4_ENCRYPTION` | y | fs/ext4/Kconfig | 整条链无引用 |
| `CONFIG_EXT4_FS_ENCRYPTION` | y | fs/ext4/Kconfig | 整条链无引用 |
| `CONFIG_EXT4_FS_POSIX_ACL` | y | fs/ext4/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_EXT4_FS_SECURITY` | y | fs/ext4/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_EXT4_USE_FOR_EXT2` | y | fs/ext4/Kconfig | 整条链无引用 |
| `CONFIG_F2FS_FS_POSIX_ACL` | y | fs/f2fs/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_F2FS_FS_SECURITY` | y | fs/f2fs/Kconfig | 整条链无引用 |
| `CONFIG_F2FS_FS_XATTR` | y | fs/f2fs/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_F2FS_STAT_FS` | y | fs/f2fs/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_FAIR_GROUP_SCHED` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_FB` | y | drivers/video/fbdev/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_FB_CFB_COPYAREA` | y | drivers/video/fbdev/Kconfig | 整条链无引用 |
| `CONFIG_FB_CFB_FILLRECT` | y | drivers/video/fbdev/Kconfig | 整条链无引用 |
| `CONFIG_FB_CFB_IMAGEBLIT` | y | drivers/video/fbdev/Kconfig | 整条链无引用 |
| `CONFIG_FB_CMDLINE` | y | drivers/video/fbdev/Kconfig | 整条链无引用 |
| `CONFIG_FB_MODE_HELPERS` | y | drivers/video/fbdev/Kconfig | 整条链无引用 |
| `CONFIG_FB_NOTIFY` | y | drivers/video/fbdev/Kconfig | 整条链无引用 |
| `CONFIG_FIB_RULES` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_FIX_EARLYCON_MEM` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_FORTIFY_SOURCE` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_FRAME_POINTER` | y | arch/arm/Kconfig.debug | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_FSL_ERRATUM_A008585` | y | drivers/clocksource/Kconfig | 整条链无引用 |
| `CONFIG_FS_ENCRYPTION_ALGS` | y | fs/crypto/Kconfig | 整条链无引用 |
| `CONFIG_FS_ENCRYPTION_INLINE_CRYPT` | y | fs/crypto/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_FTRACE` | y | kernel/trace/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_FUTEX` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_FUTEX_PI` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_FW_LOADER_USER_HELPER` | y | drivers/base/firmware_loader/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_FW_LOADER_USER_HELPER_FALLBACK` | y | drivers/base/firmware_loader/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_BUG` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_BUG_RELATIVE_POINTERS` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_CALIBRATE_DELAY` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_CLOCKEVENTS_BROADCAST` | y | kernel/time/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_GENERIC_CPU_AUTOPROBE` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_CPU_VULNERABILITIES` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_CSUM` | y | arch/arc/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_GETTIMEOFDAY` | y | lib/vdso/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_GENERIC_HWEIGHT` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_IDLE_POLL_SETUP` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_IRQ_EFFECTIVE_AFF_MASK` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_IRQ_MULTI_HANDLER` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_IRQ_PROBE` | y | arch/hexagon/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_IRQ_SHOW` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_IRQ_SHOW_LEVEL` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_MSI_IRQ_DOMAIN` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_SCHED_CLOCK` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_SMP_IDLE_THREAD` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_TIME_VSYSCALL` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_GENERIC_TRACER` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_GPIOLIB_IRQCHIP` | y | drivers/gpio/Kconfig | 整条链无引用 |
| `CONFIG_GRO_CELLS` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_HANDLE_DOMAIN_IRQ` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_HARDENED_USERCOPY` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_HARDENED_USERCOPY_FALLBACK` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_HARDEN_EL2_VECTORS` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_HARDIRQS_SW_RESEND` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_HAS_DMA` | y | arch/nios2/Kconfig | 整条链无引用 |
| `CONFIG_HAS_IOMEM` | y | arch/s390/Kconfig | 整条链无引用 |
| `CONFIG_HAS_IOPORT_MAP` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ALIGNED_STRUCT_PAGE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_AUDITSYSCALL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_BITREVERSE` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_HUGE_VMAP` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_JUMP_LABEL` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_KASAN` | y | lib/Kconfig.kasan | 整条链无引用 |
| `CONFIG_HAVE_ARCH_KASAN_SW_TAGS` | y | lib/Kconfig.kasan | 整条链无引用 |
| `CONFIG_HAVE_ARCH_KGDB` | y | lib/Kconfig.kgdb | 整条链无引用 |
| `CONFIG_HAVE_ARCH_MMAP_RND_BITS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_MMAP_RND_COMPAT_BITS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_PFN_VALID` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_PREL32_RELOCATIONS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_SECCOMP_FILTER` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_THREAD_STRUCT_WHITELIST` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_TRACEHOOK` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_TRANSPARENT_HUGEPAGE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARCH_VMAP_STACK` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_ARM_SMCCC` | y | drivers/firmware/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_CLK` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_CLK_PREPARE` | y | drivers/clk/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_CMPXCHG_DOUBLE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_CMPXCHG_LOCAL` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_CONTEXT_TRACKING` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_C_RECORDMCOUNT` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_DEBUG_BUGVERBOSE` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_HAVE_DEBUG_KMEMLEAK` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_HAVE_DMA_CONTIGUOUS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_DYNAMIC_FTRACE` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_EBPF_JIT` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_FTRACE_MCOUNT_RECORD` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_FUNCTION_GRAPH_TRACER` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_FUNCTION_TRACER` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_GCC_PLUGINS` | y | scripts/gcc-plugins/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_GENERIC_GUP` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_GENERIC_VDSO` | y | lib/vdso/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_HARDENED_USERCOPY_ALLOCATOR` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_HW_BREAKPOINT` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_IRQ_TIME_ACCOUNTING` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_KERNEL_GZIP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_KERNEL_LZ4` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_KPROBES` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_KRETPROBES` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_MEMORY_PRESENT` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_MOD_ARCH_SPECIFIC` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_NET_DSA` | y | net/dsa/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_NMI` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_PATA_PLATFORM` | y | drivers/ata/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_PERF_EVENTS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_PERF_REGS` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_PERF_USER_STACK_DUMP` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_RCU_TABLE_FREE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_REGS_AND_STACK_ACCESS_API` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_RSEQ` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_SCHED_AVG_IRQ` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_STACKPROTECTOR` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_SYSCALL_TRACEPOINTS` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_UID16` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_USERSPACE_LOW_MEMORY_KILLER` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_HAVE_VIRT_CPU_ACCOUNTING_GEN` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_HIDRAW` | y | drivers/hid/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_HIGH_RES_TIMERS` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_HISILICON_ERRATUM_161010101` | y | drivers/clocksource/Kconfig | 整条链无引用 |
| `CONFIG_HISILICON_ERRATUM_161600802` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_HOLES_IN_ZONE` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_HOTPLUG_CPU` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_HW_CONSOLE` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_HW_PERF_EVENTS` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_HZ_250` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_I2C_COMPAT` | y | drivers/i2c/Kconfig | 整条链无引用 |
| `CONFIG_I2C_HELPER_AUTO` | y | drivers/i2c/Kconfig | 整条链无引用 |
| `CONFIG_IGB_HWMON` | y | drivers/net/ethernet/intel/Kconfig | 整条链无引用 |
| `CONFIG_IIO_BUFFER` | y | drivers/iio/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_IIO_TRIGGER` | y | drivers/iio/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_IKCONFIG` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_IKCONFIG_PROC` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_IKHEADERS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_INET_DIAG_DESTROY` | y | net/ipv4/Kconfig | 整条链无引用 |
| `CONFIG_INIT_STACK_NONE` | y | security/Kconfig.hardening | 整条链无引用 |
| `CONFIG_INTEGRITY_AUDIT` | y | security/integrity/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_ION_POOL_AUTO_REFILL` | y | drivers/staging/android/ion/Kconfig | 整条链无引用 |
| `CONFIG_IPV6_MULTIPLE_TABLES` | y | net/ipv6/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_IPV6_NDISC_NODETYPE` | y | net/ipv6/Kconfig | 整条链无引用 |
| `CONFIG_IPV6_OPTIMISTIC_DAD` | y | net/ipv6/Kconfig | 整条链无引用 |
| `CONFIG_IPV6_ROUTER_PREF` | y | net/ipv6/Kconfig | 整条链无引用 |
| `CONFIG_IPV6_ROUTE_INFO` | y | net/ipv6/Kconfig | 整条链无引用 |
| `CONFIG_IPV6_SUBTREES` | y | net/ipv6/Kconfig | 整条链无引用 |
| `CONFIG_IP_ADVANCED_ROUTER` | y | net/ipv4/Kconfig | 整条链无引用 |
| `CONFIG_IP_MULTICAST` | y | net/ipv4/Kconfig | 整条链无引用 |
| `CONFIG_IP_NF_MATCH_ECN` | y | net/ipv4/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_IP_NF_MATCH_TTL` | y | net/ipv4/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_IP_NF_TARGET_NETMAP` | y | net/ipv4/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_IP_NF_TARGET_REDIRECT` | y | net/ipv4/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_IP_PNP_DHCP` | y | net/ipv4/Kconfig | 整条链无引用 |
| `CONFIG_IP_ROUTE_VERBOSE` | y | net/ipv4/Kconfig | 整条链无引用 |
| `CONFIG_IRQ_DOMAIN_HIERARCHY` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_IRQ_FORCED_THREADING` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_IRQ_TIME_ACCOUNTING` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_IRQ_WORK` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_JOYSTICK_XPAD_FF` | y | drivers/input/joystick/Kconfig | 整条链无引用 |
| `CONFIG_JOYSTICK_XPAD_LEDS` | y | drivers/input/joystick/Kconfig | 整条链无引用 |
| `CONFIG_KALLSYMS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_KALLSYMS_ALL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_KALLSYMS_BASE_RELATIVE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_KERNEL_GZIP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_KERNEL_MODE_NEON` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_KRYO_PMU_WORKAROUND` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_KUSER_HELPERS` | y | arch/arm/mm/Kconfig | 整条链无引用 |
| `CONFIG_L2TP_ETH` | y | net/l2tp/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_L2TP_IP` | y | net/l2tp/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_L2TP_V3` | y | net/l2tp/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_LDISC_AUTOLOAD` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_LIBFDT` | y | lib/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_LOCKDEP_SUPPORT` | y | arch/arc/Kconfig | 整条链无引用 |
| `CONFIG_LOCK_DEBUGGING_SUPPORT` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_LOCK_SPIN_ON_OWNER` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_LTO_NONE` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_MAGIC_SYSRQ` | y | arch/um/Kconfig | 整条链无引用 |
| `CONFIG_MAGIC_SYSRQ_SERIAL` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_MANDATORY_FILE_LOCKING` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_MAY_USE_DEVLINK` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_MDIO_BUS` | y | drivers/net/phy/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_MEDIA_ATTACH` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_MEDIA_CAMERA_SUPPORT` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_MEDIA_CONTROLLER` | y | drivers/media/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_MEDIA_DIGITAL_TV_SUPPORT` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_MEDIA_RADIO_SUPPORT` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_MEDIA_SUBDRV_AUTOSELECT` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_MEDIA_TUNER` | y | drivers/media/tuners/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_MEDIA_USB_SUPPORT` | y | drivers/media/usb/Kconfig | 整条链无引用 |
| `CONFIG_MEMBARRIER` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MEMCG` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MEMCG_KMEM` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MEMCG_SWAP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MEMCG_SWAP_ENABLED` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MEMFD_CREATE` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_MEMORY_HOTPLUG_DEFAULT_ONLINE` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_MEMORY_HOTPLUG_MOVABLE_NODE` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_MEMORY_HOTPLUG_SPARSE` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_MEMORY_HOTREMOVE` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_MISC_FILESYSTEMS` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_MITIGATE_SPECTRE_BRANCH_HISTORY` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_MMC_BLOCK_DEFERRED_RESUME` | y | drivers/mmc/core/Kconfig | 整条链无引用 |
| `CONFIG_MMC_SDHCI_BH201` | y | drivers/mmc/host/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_MMC_SDHCI_IO_ACCESSORS` | y | drivers/mmc/host/Kconfig | 整条链无引用 |
| `CONFIG_MMU` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_MODULES` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULES_TREE_LOOKUP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULES_USE_ELF_RELA` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_MODULE_FORCE_LOAD` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULE_FORCE_UNLOAD` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULE_SIG` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULE_SIG_ALL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULE_SIG_SHA512` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODULE_UNLOAD` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MODVERSIONS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MSM_PM` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_MSM_SUBSYSTEM_RESTART` | y | drivers/soc/qcom/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_MULTIUSER` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_MUTEX_SPIN_ON_OWNER` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_NAMESPACES` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_NEED_DMA_MAP_STATE` | y | kernel/dma/Kconfig | 整条链无引用 |
| `CONFIG_NEED_SG_DMA_LENGTH` | y | kernel/dma/Kconfig | 整条链无引用 |
| `CONFIG_NETDEVICES` | y | drivers/net/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_ADVANCED` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_FAMILY_ARP` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_FAMILY_BRIDGE` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_INGRESS` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_XT_MATCH_CONNMARK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_XT_MATCH_MARK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_XT_MATCH_QUOTA2_LOG` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_XT_TARGET_CONNMARK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_XT_TARGET_MARK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETFILTER_XT_TARGET_NOTRACK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NETWORK_FILESYSTEMS` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_NETWORK_SECMARK` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NET_CORE` | y | drivers/net/Kconfig | 整条链无引用 |
| `CONFIG_NET_EGRESS` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NET_FLOW_LIMIT` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NET_INGRESS` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NET_KEY` | y | net/xfrm/Kconfig | 整条链无引用 |
| `CONFIG_NET_NS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_NET_PTP_CLASSIFY` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NET_RX_BUSY_POLL` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_NF_CONNTRACK_EVENTS` | y | net/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NF_CONNTRACK_MARK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NF_CONNTRACK_PROCFS` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NF_CONNTRACK_SECMARK` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NF_CT_PROTO_DCCP` | y | net/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NF_CT_PROTO_SCTP` | y | net/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NF_CT_PROTO_UDPLITE` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NF_NAT_MASQUERADE_IPV4` | y | net/ipv4/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NF_NAT_NEEDED` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NF_NAT_PROTO_DCCP` | y | net/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NF_NAT_PROTO_SCTP` | y | net/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NF_NAT_PROTO_UDPLITE` | y | net/netfilter/Kconfig | 整条链无引用 |
| `CONFIG_NF_NAT_REDIRECT` | y | net/netfilter/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_NL80211_TESTMODE` | y | net/wireless/Kconfig | 整条链无引用 |
| `CONFIG_NO_BOOTMEM` | y | arch/x86/Kconfig | 整条链无引用 |
| `CONFIG_NO_HZ` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_NO_HZ_COMMON` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_NO_HZ_IDLE` | y | kernel/time/Kconfig | 整条链无引用 |
| `CONFIG_OKL4_GUEST` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_OKL4_VTTY_CONSOLE` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_OLD_SIGSUSPEND3` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_OVERLAY_FS_REDIRECT_ALWAYS_FOLLOW` | y | fs/overlayfs/Kconfig | 整条链无引用 |
| `CONFIG_OVERRIDE_MEMORY_LIMIT` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_PAGE_COUNTER` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PANIC_ON_REFCOUNT_ERROR` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_PANIC_ON_SSR_NOTIF_TIMEOUT` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_PARTITION_ADVANCED` | y | block/partitions/Kconfig | 整条链无引用 |
| `CONFIG_PCI` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_PCI_DOMAINS` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_PCI_DOMAINS_GENERIC` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_PCI_MSI_IRQ_DOMAIN` | y | drivers/pci/Kconfig | 整条链无引用 |
| `CONFIG_PCI_QUIRKS` | y | arch/s390/Kconfig | 整条链无引用 |
| `CONFIG_PCI_SYSCALL` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_PERF_EVENTS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PHYS_ADDR_T_64BIT` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_PLAYSTATION_FF` | y | drivers/hid/Kconfig | 整条链无引用 |
| `CONFIG_PM` | y | arch/m68k/Kconfig | 整条链无引用 |
| `CONFIG_PM_CLK` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_PM_GENERIC_DOMAINS` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_PM_GENERIC_DOMAINS_OF` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_PM_GENERIC_DOMAINS_SLEEP` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_PM_SLEEP` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_PM_SLEEP_SMP` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_POSIX_TIMERS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PREEMPT` | y | kernel/Kconfig.preempt | 整条链无引用 |
| `CONFIG_PREEMPT_COUNT` | y | kernel/Kconfig.preempt | 整条链无引用 |
| `CONFIG_PREVENT_FIRMWARE_BUILD` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_PRINTK` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PRINTK_NMI` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PRINTK_TIME` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_PRINT_QUOTA_WARNING` | y | fs/quota/Kconfig | 整条链无引用 |
| `CONFIG_PROC_PAGE_MONITOR` | y | fs/proc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_PROC_PID_CPUSET` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PROC_SYSCTL` | y | fs/proc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_PROFILING` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_PSI` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_BUS_CONFIG_RPMH` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_FALKOR_ERRATUM_1003` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_FALKOR_ERRATUM_1009` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_FALKOR_ERRATUM_E1041` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_FORCE_WDOG_BITE_ON_PANIC` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_GDSC` | y | drivers/clk/qcom/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_QCOM_INITIAL_LOGBUF` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_KGSL_IOMMU` | y | drivers/gpu/msm/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_QCOM_QDF2400_ERRATUM_0065` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_QCOM_QHEE_ENABLE_MEM_PROTECTION` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_QUEUED_RWLOCKS` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_QUEUED_SPINLOCKS` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_RADIO_ADAPTERS` | y | drivers/media/radio/Kconfig | 整条链无引用 |
| `CONFIG_RANDOMIZE_BASE` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_RANDOMIZE_MODULE_REGION_FULL` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_RCU_EXPERT` | y | kernel/rcu/Kconfig | 整条链无引用 |
| `CONFIG_RCU_FAST_NO_HZ` | y | kernel/rcu/Kconfig | 整条链无引用 |
| `CONFIG_RCU_NOCB_CPU` | y | kernel/rcu/Kconfig | 整条链无引用 |
| `CONFIG_RCU_STALL_COMMON` | y | kernel/rcu/Kconfig | 整条链无引用 |
| `CONFIG_RD_BZIP2` | y | usr/Kconfig | 整条链无引用 |
| `CONFIG_RD_GZIP` | y | usr/Kconfig | 整条链无引用 |
| `CONFIG_RD_LZMA` | y | usr/Kconfig | 整条链无引用 |
| `CONFIG_REED_SOLOMON_DEC8` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_REFCOUNT_FULL` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_REGMAP_WCD_IRQ` | y | drivers/base/regmap/Kconfig | 整条链无引用 |
| `CONFIG_RELOCATABLE` | y | arch/arm64/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_RFKILL_LEDS` | y | net/rfkill/Kconfig | 整条链无引用 |
| `CONFIG_RFKILL_PM` | y | net/rfkill/Kconfig | 整条链无引用 |
| `CONFIG_RFS_ACCEL` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_RPS` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_RSEQ` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_RTC_I2C_AND_SPI` | y | drivers/rtc/Kconfig | 整条链无引用 |
| `CONFIG_RTC_INTF_DEV` | y | drivers/rtc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_RTC_INTF_PROC` | y | drivers/rtc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_RTC_INTF_SYSFS` | y | drivers/rtc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_RTC_NVMEM` | y | drivers/rtc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_RT_MUTEXES` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_RUNTIME_TESTING_MENU` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_RWSEM_PRIO_AWARE` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_RWSEM_SPIN_ON_OWNER` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_RWSEM_XCHGADD_ALGORITHM` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_SCHEDSTATS` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_SCHED_AUTOGROUP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SCHED_CORE_CTL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SCHED_DEBUG` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_SCHED_HRTICK` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_SCHED_INFO` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_SCHED_MC` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_SCHED_TUNE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SCHED_WALT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SCSI_CONSTANTS` | y | drivers/scsi/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SCSI_DMA` | y | drivers/scsi/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SCSI_LOGGING` | y | drivers/scsi/Kconfig | 整条链无引用 |
| `CONFIG_SCSI_LOWLEVEL` | y | drivers/scsi/Kconfig | 整条链无引用 |
| `CONFIG_SCSI_MOD` | y | drivers/scsi/Kconfig | 整条链无引用 |
| `CONFIG_SCSI_MQ_DEFAULT` | y | drivers/scsi/Kconfig | 整条链无引用 |
| `CONFIG_SCSI_PROC_FS` | y | drivers/scsi/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SCSI_SCAN_ASYNC` | y | drivers/scsi/Kconfig | 整条链无引用 |
| `CONFIG_SCSI_UFS_CRYPTO` | y | drivers/scsi/ufs/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SCSI_UFS_CRYPTO_QTI` | y | drivers/scsi/ufs/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SCTP_COOKIE_HMAC_MD5` | y | net/sctp/Kconfig | 整条链无引用 |
| `CONFIG_SCTP_DEFAULT_COOKIE_HMAC_MD5` | y | net/sctp/Kconfig | 整条链无引用 |
| `CONFIG_SECCOMP` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_SECCOMP_FILTER` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_SECTION_MISMATCH_WARN_ONLY` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_SECURITY_APPARMOR_HASH` | y | security/apparmor/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SECURITY_APPARMOR_HASH_DEFAULT` | y | security/apparmor/Kconfig | 整条链无引用 |
| `CONFIG_SECURITY_NETWORK` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_SECURITY_PATH` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_SECURITY_SELINUX_AVC_STATS` | y | security/selinux/Kconfig | 整条链无引用 |
| `CONFIG_SECURITY_SELINUX_DEVELOP` | y | security/selinux/Kconfig | 整条链无引用 |
| `CONFIG_SELECT_MEMORY_MODEL` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_SERIAL_MSM_GENI_HALF_SAMPLING` | y | drivers/tty/serial/Kconfig | 整条链无引用 |
| `CONFIG_SETEND_EMULATION` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_SETUP_SSR_NOTIF_TIMEOUTS` | y | drivers/soc/qcom/Kconfig | 整条链无引用 |
| `CONFIG_SGL_ALLOC` | y | lib/Kconfig | 整条链无引用 |
| `CONFIG_SHMEM` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SIGNALFD` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SLAB_FREELIST_HARDENED` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SLAB_FREELIST_RANDOM` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SLAB_MERGE_DEFAULT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SLUB` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SLUB_CPU_PARTIAL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SMP` | y | arch/alpha/Kconfig | 整条链无引用 |
| `CONFIG_SND_DRIVERS` | y | sound/drivers/Kconfig | 整条链无引用 |
| `CONFIG_SND_DYNAMIC_MINORS` | y | sound/core/Kconfig | 整条链无引用 |
| `CONFIG_SND_JACK` | y | sound/core/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_JACK_INPUT_DEV` | y | sound/core/Kconfig | 整条链无引用 |
| `CONFIG_SND_PCI` | y | sound/pci/Kconfig | 整条链无引用 |
| `CONFIG_SND_PCM_ELD` | y | sound/core/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_PCM_IEC958` | y | sound/core/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_PCM_TIMER` | y | sound/core/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_PROC_FS` | y | sound/core/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_SOC_COMPRESS` | y | sound/soc/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_SOC_I2C_AND_SPI` | y | sound/soc/codecs/Kconfig | 整条链无引用 |
| `CONFIG_SND_SPI` | y | sound/spi/Kconfig | 整条链无引用 |
| `CONFIG_SND_SUPPORT_OLD_API` | y | sound/core/Kconfig | 整条链无引用 |
| `CONFIG_SND_USB` | y | sound/usb/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SND_VERBOSE_PROCFS` | y | sound/core/Kconfig | 整条链无引用 |
| `CONFIG_SOCIONEXT_SYNQUACER_PREITS` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_SOCKEV_NLMCAST` | y | net/Kconfig | 整条链无引用 |
| `CONFIG_SOCK_CGROUP_DATA` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SONY_FF` | y | drivers/hid/Kconfig | 整条链无引用 |
| `CONFIG_SPARSEMEM_EXTREME` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_SPARSEMEM_MANUAL` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_SPARSEMEM_VMEMMAP_ENABLE` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_SPARSE_IRQ` | y | kernel/irq/Kconfig | 整条链无引用 |
| `CONFIG_SPECULATIVE_PAGE_FAULT` | y | mm/Kconfig | 整条链无引用 |
| `CONFIG_SPINEL_CHARGER` | y | drivers/power/supply/qcom/Kconfig | 整条链无引用 |
| `CONFIG_SPS_SUPPORT_NDP_BAM` | y | drivers/platform/msm/Kconfig | 整条链无引用 |
| `CONFIG_SRCU` | y | kernel/rcu/Kconfig | 整条链无引用 |
| `CONFIG_SSB_POSSIBLE` | y | drivers/ssb/Kconfig | 整条链无引用 |
| `CONFIG_STACKPROTECTOR` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_STACKPROTECTOR_STRONG` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_STACKTRACE` | y | lib/Kconfig.debug | 整条链无引用 |
| `CONFIG_STACKTRACE_SUPPORT` | y | arch/arc/Kconfig | 整条链无引用 |
| `CONFIG_STANDALONE` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_STATIC_USERMODEHELPER` | y | security/Kconfig | 整条链无引用 |
| `CONFIG_STRICT_KERNEL_RWX` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_STRICT_MODULE_RWX` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_SUSPEND_FREEZER` | y | kernel/power/Kconfig | 整条链无引用 |
| `CONFIG_SWAP` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SWPHY` | y | drivers/net/phy/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_SWP_EMULATION` | y | arch/arm64/Kconfig | 整条链无引用 |
| `CONFIG_SYSCTL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SYSCTL_EXCEPTION_TRACE` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SYSFS_SYSCALL` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SYSTEM_DATA_VERIFICATION` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_SYS_SUPPORTS_HUGETLBFS` | y | arch/arm/Kconfig | 整条链无引用 |
| `CONFIG_TASKSTATS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_TASKS_RCU` | y | kernel/rcu/Kconfig | 整条链无引用 |
| `CONFIG_TASK_IO_ACCOUNTING` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_TASK_XACCT` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_THERMAL_DEFAULT_GOV_STEP_WISE` | y | drivers/thermal/Kconfig | 整条链无引用 |
| `CONFIG_THERMAL_GOV_LOW_LIMITS` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_THERMAL_GOV_STEP_WISE` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_THERMAL_GOV_USER_SPACE` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_THERMAL_HWMON` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_THERMAL_OF` | y | drivers/thermal/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_THERMAL_WRITABLE_TRIPS` | y | drivers/thermal/Kconfig | 整条链无引用 |
| `CONFIG_THREAD_INFO_IN_TASK` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_TICK_CPU_ACCOUNTING` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_TIMERFD` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_TMPFS` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_TMPFS_POSIX_ACL` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_TMPFS_XATTR` | y | fs/Kconfig | 整条链无引用 |
| `CONFIG_TOUCHSCREEN_SYNAPTICS_DSX_FW_UPDATE_EXTRA_SYSFS` | y | drivers/input/touchscreen/synaptics_dsx/Kconfig | 整条链无引用 |
| `CONFIG_TRACEPOINTS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_TRACE_IRQFLAGS_SUPPORT` | y | arch/arc/Kconfig | 整条链无引用 |
| `CONFIG_TRACING_EVENTS_GPIO` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_TRACING_SUPPORT` | y | kernel/trace/Kconfig | 整条链无引用 |
| `CONFIG_TTY_FLUSH_LOCAL_ECHO` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_UEVENT_HELPER` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_UID16` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_UNINLINE_SPIN_UNLOCK` | y | kernel/Kconfig.locks | 整条链无引用 |
| `CONFIG_UPROBES` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_USB_ANNOUNCE_NEW_DEVICES` | y | drivers/usb/core/Kconfig | 整条链无引用 |
| `CONFIG_USB_ARCH_HAS_HCD` | y | drivers/usb/Kconfig | 整条链无引用 |
| `CONFIG_USB_ARMLINUX` | y | drivers/net/usb/Kconfig | 整条链无引用 |
| `CONFIG_USB_BELKIN` | y | drivers/net/usb/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_ACC` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_AUDIO_SRC` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_CCID` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_CDEV` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_DIAG` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_FS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_HID` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_MIDI` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_MTP` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_PTP` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_QDSS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_UAC1` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_UAC2` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_F_UVC` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_MASS_STORAGE` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_NCM` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_RNDIS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_CONFIGFS_UEVENT` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_DEFAULT_PERSIST` | y | drivers/usb/core/Kconfig | 整条链无引用 |
| `CONFIG_USB_DWC3_DUAL_ROLE` | y | drivers/usb/dwc3/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_USB_EHCI_TT_NEWSCHED` | y | drivers/usb/host/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_ACC` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_AUDIO_SRC` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_CCID` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_CDEV` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_DIAG` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_FS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_HID` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_MASS_STORAGE` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_MIDI` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_MTP` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_NCM` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_PTP` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_QDSS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_RNDIS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_UAC1` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_UAC2` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_F_UVC` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_HIDDEV` | y | drivers/hid/usbhid/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_USB_ISP1760_HCD` | y | drivers/usb/isp1760/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_USB_ISP1760_HOST_ROLE` | y | drivers/usb/isp1760/Kconfig | 整条链无引用 |
| `CONFIG_USB_NET_CDC_SUBSET` | y | drivers/net/usb/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_USB_OHCI_LITTLE_ENDIAN` | y | drivers/usb/Kconfig | 整条链无引用 |
| `CONFIG_USB_RNDIS` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_U_AUDIO` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_U_ETHER` | y | drivers/usb/gadget/Kconfig | 整条链无引用 |
| `CONFIG_USB_VIDEO_CLASS_INPUT_EVDEV` | y | drivers/media/usb/uvc/Kconfig | 整条链无引用 |
| `CONFIG_UTS_NS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_V4L_PLATFORM_DRIVERS` | y | drivers/media/platform/Kconfig | 整条链无引用 |
| `CONFIG_VIDEO_ADV_DEBUG` | y | drivers/media/v4l2-core/Kconfig | 整条链无引用 |
| `CONFIG_VIDEO_FIXED_MINOR_RANGES` | y | drivers/media/v4l2-core/Kconfig | 整条链无引用 |
| `CONFIG_VIDEO_V4L2_SUBDEV_API` | y | drivers/media/Kconfig | 整条链无引用 |
| `CONFIG_VIDEO_V4L2_VIDEOBUF2_CORE` | y | drivers/media/platform/Kconfig | 整条链无引用 |
| `CONFIG_VIRTIO_MENU` | y | drivers/virtio/Kconfig | 整条链无引用 |
| `CONFIG_VMAP_STACK` | y | arch/Kconfig | 整条链无引用 |
| `CONFIG_VM_EVENT_COUNTERS` | y | init/Kconfig | 整条链无引用 |
| `CONFIG_VSERVICES_CHAR_DEV` | y | drivers/vservices/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_VSERVICES_LOCK_DEBUG` | y | drivers/vservices/Kconfig | 整条链无引用 |
| `CONFIG_VSERVICES_PROTOCOL_BLOCK_CLIENT` | y | drivers/vservices/protocol/Kconfig | 整条链无引用 |
| `CONFIG_VSERVICES_PROTOCOL_BLOCK_SERVER` | y | drivers/vservices/protocol/Kconfig | 整条链无引用 |
| `CONFIG_VSERVICES_PROTOCOL_SERIAL_CLIENT` | y | drivers/vservices/protocol/Kconfig | 整条链无引用 |
| `CONFIG_VSERVICES_PROTOCOL_SERIAL_SERVER` | y | drivers/vservices/protocol/Kconfig | 整条链无引用 |
| `CONFIG_VT` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_VT_CONSOLE` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_VT_CONSOLE_SLEEP` | y | drivers/tty/Kconfig | 整条链无引用 |
| `CONFIG_WANT_DEV_COREDUMP` | y | drivers/base/Kconfig | 整条链无引用 |
| `CONFIG_WIL6210_IPA` | y | drivers/net/wireless/ath/wil6210/Kconfig | Makefile 有引用但非 obj 规则(功能开关) |
| `CONFIG_WIL6210_ISR_COR` | y | drivers/net/wireless/ath/wil6210/Kconfig | 整条链无引用 |
| `CONFIG_WIL6210_PLATFORM_MSM` | y | drivers/net/wireless/ath/wil6210/Kconfig | 整条链无引用 |
| `CONFIG_WIL6210_WRITE_IOCTL` | y | drivers/net/wireless/ath/wil6210/Kconfig | 整条链无引用 |
| `CONFIG_WIRELESS_EXT` | y | net/wireless/Kconfig | 整条链无引用 |
| `CONFIG_XPS` | y | net/Kconfig | 整条链无引用 |
