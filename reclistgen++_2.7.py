#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
录音表与oto模板生成器
版本：2.7.0 (Debug enhanced)
"""
import configparser
import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from collections import defaultdict

# ===== 全局变量 =====
root = tk.Tk()
root.withdraw()

rules_file_path = tk.StringVar()
mode_var = tk.StringVar(value="vccv-cvvc")
generation_mode_var = tk.StringVar(value="none")
language_var = tk.StringVar(value="zh")
separator_format_var = tk.StringVar(value="R-dash")
oto_sort_var = tk.StringVar(value="order")

current_language = "zh"
text = {}
config_file = "reclistgen++_config.ini"
language_file = "languages.ini"
available_languages = []
recording_list = []
oto_entries = []

# ===== 工具函数 =====
def natural_sort_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def get_text(key):
    return text.get(key, key)

def convert_separator_display(entry, sep_format):
    """
    将内部条目字符串转为用户显示/导出的格式。
    去除首尾的 '-' 和 '_'，内部 '-' 根据 sep_format 替换为 'R' 或保留 '-'。
    """
    # 去除首尾空白和下划线
    entry = entry.strip('_').strip()
    # 去除首尾 '-' 和 '_'
    entry = entry.strip('-_')
    # 内部 '-' 替换
    if sep_format == "R-dash":
        return entry.replace('-', 'R')
    else:
        return entry

# ===== 语言文件加载 =====
def load_language_file(lang_file="languages.ini"):
    global text, current_language, available_languages
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    try:
        if not os.path.exists(lang_file):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            lang_file = os.path.join(base_dir, "languages.ini")
            if not os.path.exists(lang_file):
                raise FileNotFoundError(f"语言文件未找到: {lang_file}")
        with open(lang_file, 'r', encoding='utf-8') as f:
            config.read_file(f)
        available_languages = config.sections()
        if not available_languages:
            raise ValueError("语言文件中没有语言节")
        if current_language not in config:
            current_language = available_languages[0]
        text = {}
        for key, value in config[current_language].items():
            text[key] = value
        return available_languages
    except Exception as e:
        text = {
            "title": "录音表与oto模板生成器",
            "rules_file_label": "规则文件",
            "browse_button": "浏览...",
            "generate_button": "生成",
            "export_reclist_button": "导出录音表",
            "export_oto_button": "导出 oto",
            "settings_label": "设置",
            "mode_label": "录音模式",
            "generation_mode_label": "强制生成模式",
            "max_syllables_label": "最大音节数",
            "bpm_label": "BPM",
            "leading_silence_label": "前导静音 (ms)",
            "max_alternatives_label": "最大后备条目名",
            "merge_short_entries_label": "合并短条目",
            "prioritize_semi_vowels_label": "半元音优先生成",
            "prioritize_vowel_transitions_label": "纯元音优先生成",
            "transition_generation_label": "衔接部产生",
            "transition_generation_all": "产生衔接部分",
            "transition_generation_none": "不做衔接部分",
            "first_sound_label": "开头音设置",
            "first_sound_none": "不确保开头音",
            "first_sound_onset": "确保开头整音",
            "first_sound_consonant": "确保开头辅音",
            "ensure_coda_r_label": "确保尾音到R",
            "ensure_vowel_link_label": "确保纯元音链接",
            "ensure_all_syllables_forced_label": "强制生成部分确保所有完整发音存在",
            "ensure_all_syllables_standard_label": "标准生成部分确保所有完整发音存在",
            "generate_frame_label": "顺带生成",
            "generate_coda_consonant_label": "尾音到辅音",
            "generate_coda_onset_label": "尾音到整音",
            "generate_onset_consonant_label": "整音到辅音",
            "generate_onset_label": "单独整音",
            "generate_onset_vccv_label": "单独整音（纯元音）",
            "semi_vowels_label": "半元音列表（逗号分隔）",
            "language_label": "语言",
            "line_count_reclist": "录音表行数: {}",
            "line_count_oto": "oto行数: {}",
            "recording_list": "录音表",
            "oto_configuration": "oto 配置",
            "removed_title": "被剔除条目",
            "unused_syllables_title": "未使用的完整发音",
            "debug_title": "诊断",
            "load_config_button": "加载配置",
            "save_config_button": "保存配置",
            "success": "成功",
            "error": "错误",
            "warning": "警告",
            "first_sound_warning": "您选择了“不确保开头音”，可能导致开头音素缺失！",
            "coda_r_warning": "您选择了“不确保尾音到R”，可能导致结尾音素缺失！",
            "recording_list_saved": "录音表已保存至 {}",
            "oto_configuration_saved": "oto 已保存至 {}",
            "failed_to_export_recording_list": "导出录音表失败: {}",
            "failed_to_export_oto_configuration": "导出 oto 失败: {}",
            "invalid_rule_file": "无效的规则文件",
            "missing_coda_onset": "coda 或 onset 字段为空",
            "config_saved": "配置已保存至 {}",
            "config_load_failed": "加载配置失败: {}",
            "config_save_failed": "保存配置失败: {}",
            "copy_all": "复制全部",
            "removed_count": "共剔除 {} 条",
            "separator_label": "休止符格式",
            "oto_sort_label": "oto 排序",
            "oto_sort_order": "顺序排列",
            "oto_sort_category": "分类排列",
            "enable_generate_extra": "启用顺带生成",
            "protect_frame": "保护",
            "priority_frame": "优先级",
            "other_frame": "其他",
            "generate_frame": "顺带生成",
            "no_rules_file": "请先选择规则文件",
            "parse_rules_failed": "解析规则文件失败: {}",
            "copied_to_clipboard": "已复制到剪贴板",
            "transition_mode_reminder_title": "衔接部设置提醒",
            "transition_mode_reminder_text": "切换模式后，请注意“衔接部产生”勾选框的设置。\nVCCV-CVVC 模式通常需要勾选“产生衔接部分”，其他模式可根据需要自行选择。",
            "separator_R_dash": "R 休止符",
            "separator_dash_dash": "- 休止符",
            "unique_entry_strategy_label": "弱势发音补全策略",
            "unique_entry_strategy_replace": "替换重复条目",
            "unique_entry_strategy_backup_alias": "强制后备别名",
            "first_onset_as_normal_label": "开头整音视为普通整音",
            "redundancy_mode_label": "录音表冗余模式",
            "redundancy_mode_active_removal": "积极剔除",
            "redundancy_mode_keep_all_syllables": "确保全局完整发音完整",
            "global_sort_reclist_label": "录音表排序",
            "global_sort_grouped": "分组排序",
            "global_sort_global": "全局自然排序",
            "generation_mode_none": "不强制",
            "generation_mode_repeat": "重复",
            "generation_mode_interval": "间隔",
            "generation_mode_sequence": "顺序",
        }
        return ["zh"]

# ===== 配置加载/保存 =====
def load_config_file(filepath):
    config = configparser.ConfigParser()
    settings = {
        'max_syllables_per_sentence': 8,
        'mode': 'vccv-cvvc',
        'separator_format': 'R-dash',
        'oto_sort': 'order',
        'merge_short_entries': False,
        'bpm': 120,
        'leading_silence': 100,
        'max_alternatives': 0,
        'use_consonant_for_first_syllable': False,
        'semi_vowels': 'v,w,y',
        'prioritize_semi_vowels': False,
        'prioritize_vowel_transitions': False,
        'prioritize_unique_entries_oto': False,
        'transition_generation': 'all',
        'first_sound': 'onset',
        'ensure_coda_r': True,
        'ensure_vowel_link': True,
        'ensure_all_syllables_forced': True,
        'ensure_all_syllables_standard': True,
        'generate_coda_consonant': False,
        'generate_coda_onset': False,
        'generate_onset_consonant': False,
        'generate_onset': False,
        'generation_mode': 'none',
        'unique_entry_strategy': 'replace',
        'first_onset_as_normal': False,
        'redundancy_mode': 'active_removal',
        'global_sort_reclist': 'grouped',
    }
    try:
        config.read(filepath, encoding='utf-8')
        if 'GENERAL' in config:
            g = config['GENERAL']
            settings['max_syllables_per_sentence'] = int(g.get('max_syllables_per_sentence', 8))
            settings['mode'] = g.get('mode', 'vccv-cvvc')
            settings['separator_format'] = g.get('separator_format', 'R-dash')
            settings['oto_sort'] = g.get('oto_sort', 'order')
            settings['merge_short_entries'] = g.getboolean('merge_short_entries', False)
            settings['generation_mode'] = g.get('generation_mode', 'none')
            settings['first_sound'] = g.get('first_sound', 'onset')
            settings['ensure_coda_r'] = g.getboolean('ensure_coda_r', True)
            settings['ensure_vowel_link'] = g.getboolean('ensure_vowel_link', True)
            settings['ensure_all_syllables_forced'] = g.getboolean('ensure_all_syllables_forced', True)
            settings['ensure_all_syllables_standard'] = g.getboolean('ensure_all_syllables_standard', True)
        if 'OTO' in config:
            o = config['OTO']
            settings['bpm'] = int(o.get('bpm', 120))
            settings['leading_silence'] = int(o.get('leading_silence', 100))
            settings['max_alternatives'] = int(o.get('max_alternatives', 1))
            settings['use_consonant_for_first_syllable'] = o.getboolean('use_consonant_for_first_syllable', False)
            settings['generate_coda_consonant'] = o.getboolean('generate_coda_consonant', False)
            settings['generate_coda_onset'] = o.getboolean('generate_coda_onset', False)
            settings['generate_onset_consonant'] = o.getboolean('generate_onset_consonant', False)
            settings['generate_onset'] = o.getboolean('generate_onset', False)
        if 'PHONEME' in config:
            p = config['PHONEME']
            settings['semi_vowels'] = p.get('semi_vowels', 'v,w,y')
        if 'OPTIONS' in config:
            opt = config['OPTIONS']
            settings['prioritize_semi_vowels'] = opt.getboolean('prioritize_semi_vowels', False)
            settings['prioritize_vowel_transitions'] = opt.getboolean('prioritize_vowel_transitions', False)
            settings['transition_generation'] = opt.get('transition_generation', 'all')
            settings['unique_entry_strategy'] = opt.get('unique_entry_strategy', 'replace')
            settings['first_onset_as_normal'] = opt.getboolean('first_onset_as_normal', False)
            settings['redundancy_mode'] = opt.get('redundancy_mode', 'active_removal')
            raw_sort = opt.get('global_sort_reclist', 'grouped')
            if raw_sort in ('true', 'True', '1'):
                settings['global_sort_reclist'] = 'global'
            elif raw_sort in ('false', 'False', '0'):
                settings['global_sort_reclist'] = 'grouped'
            elif raw_sort in ('grouped', 'global'):
                settings['global_sort_reclist'] = raw_sort
            else:
                settings['global_sort_reclist'] = 'grouped'
    except Exception as e:
        print(f"配置加载失败: {e}")
    return settings

def save_config_file(filepath, settings):
    config = configparser.ConfigParser()
    config['GENERAL'] = {
        'max_syllables_per_sentence': str(settings['max_syllables_per_sentence']),
        'mode': settings['mode'],
        'separator_format': settings['separator_format'],
        'oto_sort': settings['oto_sort'],
        'merge_short_entries': str(settings['merge_short_entries']).lower(),
        'generation_mode': settings.get('generation_mode', 'none'),
        'first_sound': settings['first_sound'],
        
        'ensure_coda_r': str(settings['ensure_coda_r']).lower(),
        'ensure_vowel_link': str(settings['ensure_vowel_link']).lower(),
        'ensure_all_syllables_forced': str(settings['ensure_all_syllables_forced']).lower(),
        'ensure_all_syllables_standard': str(settings['ensure_all_syllables_standard']).lower()
    }
    config['OTO'] = {
        'bpm': str(settings['bpm']),
        'leading_silence': str(settings['leading_silence']),
        'max_alternatives': str(settings['max_alternatives']),
        'use_consonant_for_first_syllable': 'false',
        'generate_coda_consonant': str(settings['generate_coda_consonant']).lower(),
        'generate_coda_onset': str(settings['generate_coda_onset']).lower(),
        'generate_onset_consonant': str(settings['generate_onset_consonant']).lower(),
        'generate_onset': str(settings['generate_onset']).lower()
    }
    config['PHONEME'] = {
        'semi_vowels': settings['semi_vowels']
    }
    config['OPTIONS'] = {
        'prioritize_semi_vowels': str(settings['prioritize_semi_vowels']).lower(),
        'prioritize_vowel_transitions': str(settings['prioritize_vowel_transitions']).lower(),
        'transition_generation': settings['transition_generation'],
        'unique_entry_strategy': settings.get('unique_entry_strategy', 'replace'),
        'first_onset_as_normal': str(settings.get('first_onset_as_normal', False)).lower(),
        'redundancy_mode': settings.get('redundancy_mode', 'active_removal'),
        'global_sort_reclist': settings.get('global_sort_reclist', 'grouped'),
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        config.write(f)

# ===== 规则解析 =====
class RuleParser:
    @staticmethod
    def parse(rule_file):
        rules = {}
        config = configparser.ConfigParser(allow_no_value=True, interpolation=None)
        config.optionxform = str
        try:
            config.read(rule_file, encoding='utf-8')
        except Exception as e:
            raise ValueError(f"规则文件读取失败: {e}")

        if 'RULE' not in config:
            raise ValueError("规则文件中缺少 [RULE] 节")

        pattern = re.compile(r',(?=(?:[^"]*"[^"]*")*[^"]*$)')

        for syllable, value in config['RULE'].items():
            components = [c.strip().strip('"') for c in pattern.split(value)]
            if len(components) != 4:
                raise ValueError(f"音节 {syllable} 格式错误，应包含4个字段: 辅音, 整音, transition, 尾音")

            consonant, onset, transition, coda = components

            if not onset:
                raise ValueError(f"音节 {syllable} 的整音(onset)字段为空")
            if not coda:
                raise ValueError(f"音节 {syllable} 的尾音(coda)字段为空")

            if transition:
                transition = transition.strip().strip('"')
                trans_list = [t.strip() for t in transition.split(',') if t.strip()]
            else:
                trans_list = []

            rules[syllable] = {
                'consonant': consonant.strip(),
                'onset': onset.strip(),
                'transition': trans_list,
                'coda': coda.strip()
            }
        return rules

# ===== 录音表生成核心 =====
class RecordingListGenerator:
    def __init__(self, rules, settings, debug_log=None):
        self.rules = rules
        self.settings = settings
        self.mode = settings['mode']
        self.max_syllables = settings['max_syllables_per_sentence']
        self.merge_short_entries = settings.get('merge_short_entries', False)
        self.redundancy_mode = settings.get('redundancy_mode', 'active_removal')
        self.prioritize_semi_vowels = settings['prioritize_semi_vowels']
        self.prioritize_vowel_transitions = settings['prioritize_vowel_transitions']
        self.transition_generation = settings['transition_generation']
        self.first_sound = settings['first_sound']
        self.ensure_coda_r = settings['ensure_coda_r']
        self.ensure_all_syllables_forced = settings['ensure_all_syllables_forced']
        self.ensure_all_syllables_standard = settings['ensure_all_syllables_standard']
        self.ensure_vowel_link = settings['ensure_vowel_link']
        self.semi_vowels = [x.strip() for x in settings['semi_vowels'].split(',') if x.strip()]
        self.debug_log = debug_log if debug_log is not None else []

        self.syllables = list(rules.keys())
        self.all_codas = set()
        self.syllable_usage_count = defaultdict(int)
        self.all_consonants = set()
        self.all_onsets = set()
        self.all_vowel_onsets = set()
        for syl, parts in rules.items():
            self.all_codas.add(parts['coda'])
            if parts['consonant']:
                self.all_consonants.add(parts['consonant'])
            self.all_onsets.add(parts['onset'])
            if not parts['consonant']:
                self.all_vowel_onsets.add(parts['onset'])

    def log(self, step, message):
        self.debug_log.append(f"[{step}] {message}")

    def generate(self):
        self.log(1, "开始生成录音表")
        forced = self._generate_forced()
        forced_set = set(forced)
        self.log(1, f"强制生成条目数: {len(forced)}")
        covered_combos = self._get_covered_combinations(forced)
        covered_syllables = set()
        for entry in forced:
            for s in entry.split('_'):
                if s != '-' and s != 'R':
                    covered_syllables.add(s)

        standard = []
        if self.mode != 'cv':
            standard = self._generate_standard(covered_combos, covered_syllables)
            self.log(2, f"标准生成条目数: {len(standard)}")

            # 决定是否需要补全缺失完整发音
            need_ensure_all_syllables = self.ensure_all_syllables_standard or (
                not self.ensure_all_syllables_standard and
                not self.ensure_all_syllables_forced and
                self.redundancy_mode == 'keep_all_syllables'
            )
            if need_ensure_all_syllables:
                missing_entries = self._generate_missing_syllable_entries(covered_syllables)
                standard.extend(missing_entries)
                self.log(2, f"补全缺失完整发音 {len(missing_entries)} 条")
            # 消除标准条目中因分组造成的首尾重复
            standard = self._merge_adjacent_duplicates(standard)
            self.log(2, f"标准生成条目合并后数量: {len(standard)}")
        else:
            self.log(2, "CV 模式，跳过标准生成")
        entries = forced + standard

        # 去重
        unique = []
        seen = set()
        for e in entries:
            if e not in seen:
                seen.add(e)
                unique.append(e)
        entries = unique
        self.log(3, f"去重后条目数: {len(entries)}")

        first_sound_entries = []
        if self.first_sound != 'none':
            before = set(entries)
            entries = self._ensure_first_sound_coverage(entries)
            first_sound_entries = [e for e in entries if e not in before]
            self.log(4, f"开头音补全条目数: {len(first_sound_entries)}")

        # ============ 保底补全（在合并短条目之前执行，确保短条目也能参与合并） ============

        # ---- Coda R 保底：确保每个 coda 至少一次作为条目结尾 ----
        covered_coda_r = set()
        for entry in entries:
            parts = entry.split('_')
            for i, p in enumerate(parts):
                if p == '-' or p == 'R':
                    continue
                if i == len(parts)-1 or (i+1 < len(parts) and parts[i+1] == '-'):
                    if p in self.rules:
                        covered_coda_r.add(self.rules[p]['coda'])

        missing_coda_r = set(self.all_codas) - covered_coda_r
        if missing_coda_r:
            # 候选起始音节：从已有条目中收集非缺失 coda 的音节
            starter_candidates = []
            for syl in self.syllables:
                if self.rules[syl]['coda'] not in missing_coda_r:
                    starter_candidates.append(syl)
            if not starter_candidates:
                starter_candidates = self.syllables.copy()

            starter_idx = 0
            for coda in sorted(missing_coda_r, key=natural_sort_key):
                # 找到具有该 coda 的一个音节
                candidate_syllable = next((s for s in self.syllables if self.rules[s]['coda'] == coda), None)
                if not candidate_syllable:
                    continue
                starter = starter_candidates[starter_idx % len(starter_candidates)]
                starter_idx += 1
                new_entry = f"{starter}_{candidate_syllable}"
                entries.append(new_entry)

        # ---- Onset 保底：确保每个音节至少一次处于非开头位置 ----
        # CV 模式无需此保底（单音节已满足）
        if self.mode != 'cv':
            all_covered_non_initial = set()
            for entry in entries:
                parts = entry.split('_')
                for i, p in enumerate(parts):
                    if p == '-' or p == 'R':
                        continue
                    if i > 0 and parts[i-1] != '-':
                        all_covered_non_initial.add(p)

            missing_non_initial = set(self.syllables) - all_covered_non_initial
            if missing_non_initial:
                # 候选起始音节：从已覆盖非开头的音节中选择
                starter_candidates = [s for s in self.syllables if s in all_covered_non_initial]
                if not starter_candidates:
                    starter_candidates = self.syllables.copy()

                starter_idx = 0
                missing_list = sorted(missing_non_initial, key=natural_sort_key)
                current_group = []
                for syl in missing_list:
                    if not current_group:
                        starter = starter_candidates[starter_idx % len(starter_candidates)]
                        starter_idx += 1
                        current_group.append(starter)
                    if len(current_group) < self.max_syllables:
                        current_group.append(syl)
                    else:
                        entries.append('_'.join(current_group))
                        starter = starter_candidates[starter_idx % len(starter_candidates)]
                        starter_idx += 1
                        current_group = [starter, syl]
                if len(current_group) > 1:
                    entries.append('_'.join(current_group))

        # 合并短条目（仅标准部分和保底补全，不含开头音补全）
        # CV 模式不需要合并
        if self.merge_short_entries and self.mode != 'cv':
            standard_entries = [e for e in entries if e not in forced_set and e not in first_sound_entries]
            merged_standard = self._merge_entries(standard_entries)
            entries = forced + merged_standard + first_sound_entries
            entries = list(dict.fromkeys(entries))
            self.log(5, "合并短条目完成")

        # 最终排序
        forced_final = [e for e in entries if e in forced_set]
        first_sound_final = [e for e in entries if e in first_sound_entries]
        standard_final = [e for e in entries if e not in forced_set and e not in first_sound_entries]

        forced_final.sort(key=natural_sort_key)
        first_sound_final.sort(key=natural_sort_key)
        standard_final.sort(key=natural_sort_key)

        entries = forced_final + standard_final + first_sound_final
        self.log(6, "最终排序完成")

        return entries, forced_set, first_sound_entries

    def get_end_separator(self):
        """根据 separator_format 返回结尾分隔符：R 或 -"""
        return 'R' if self.settings.get('separator_format', 'R-dash') == 'R-dash' else '-'

    def _generate_forced(self):
        mode = self.settings['generation_mode']
        if mode == 'none':
            if self.mode == 'cv':
                # CV 模式下 none 等同 sequence
                mode = 'sequence'
            else:
                self.log(1, "未启用强制生成")
                return []

        # 选择参与强制生成的音节列表
        if self.mode == 'cv':
            if self.ensure_all_syllables_forced:
                syllables = sorted(self.syllables, key=natural_sort_key)
                self.log(1, f"强制保护开启，使用全部 {len(syllables)} 个音节")
            else:
                syllables = self._select_representative_syllables_cv()
                self.log(1, f"CV 模式保护关闭，选择 {len(syllables)} 个代表性音节")
        else:
            if self.ensure_all_syllables_forced:
                syllables = sorted(self.syllables, key=natural_sort_key)
                self.log(1, f"强制保护开启，使用全部 {len(syllables)} 个音节")
            else:
                chosen = []
                for syl in self.syllables:
                    parts = self.rules[syl]
                    if not parts['consonant']:
                        chosen.append(syl)
                    elif parts['consonant'] in self.semi_vowels:
                        chosen.append(syl)
                    elif self.prioritize_vowel_transitions and not parts['consonant'] and parts['transition']:
                        chosen.append(syl)
                    elif self.prioritize_semi_vowels and parts['consonant'] in self.semi_vowels:
                        chosen.append(syl)
                if not chosen:
                    chosen = [s for s in self.syllables if not self.rules[s]['consonant']]
                syllables = chosen or self.syllables
                self.log(1, f"强制保护关闭，选择 {len(syllables)} 个代表性音节")

        # 强制生成时，音节列表始终按自然排序，不响应优先级开关
        syllables = sorted(syllables, key=natural_sort_key)

        forced = []
        if mode == 'repeat':
            for syl in syllables:
                forced.append(f"{syl}_{syl}_{syl}")
        elif mode == 'interval':
            pattern = []
            for syl in syllables:
                pattern.append(syl)
                pattern.append("-")
            if pattern and pattern[-1] == "-":
                pattern = pattern[:-1]
            current = []
            for item in pattern:
                if len(current) < self.max_syllables:
                    current.append(item)
                else:
                    if current:
                        forced.append('_'.join(current))
                    current = [item]
            if current:
                forced.append('_'.join(current))
            current = []
            for syl in syllables:
                if len(current) < self.max_syllables:
                    current.append(syl)
                else:
                    if current:
                        forced.append('_'.join(current))
                    current = [syl]
            if current:
                forced.append('_'.join(current))
        elif mode == 'sequence':
            current = []
            for syl in syllables:
                if len(current) < self.max_syllables:
                    current.append(syl)
                else:
                    if current:
                        forced.append('_'.join(current))
                    current = [syl]
            if current:
                forced.append('_'.join(current))
        return forced

    def _select_representative_syllables_cv(self):
        """CV 模式下保护关闭时，基于音素覆盖选择代表性音节。"""
        # 构建需要覆盖的目标音素集合
        target_phonemes = set()
        
        # 所有 onset 字符串必须覆盖
        target_phonemes.update(self.all_onsets)
        
        # 根据设置添加额外目标
        if self.ensure_coda_r:
            target_phonemes.update(self.all_codas)
        if self.transition_generation == 'all':
            for syl, info in self.rules.items():
                target_phonemes.update(info['transition'])
        if self.first_sound == 'consonant':
            target_phonemes.update(self.all_consonants)
            # 纯元音的 onset 也需要覆盖（作为开头整音）
            for syl, info in self.rules.items():
                if not info['consonant']:
                    target_phonemes.add(info['onset'])
        # 如果 first_sound == 'onset'，无需额外操作，因为 onset 已包含

        if not target_phonemes:
            return []

        # 构建每个音节可覆盖的音素集合
        syllable_phonemes = {}
        for syl, info in self.rules.items():
            covered = set()
            covered.add(info['onset'])
            if self.ensure_coda_r and info['coda']:
                covered.add(info['coda'])
            if self.transition_generation == 'all':
                covered.update(info['transition'])
            if self.first_sound == 'consonant' and info['consonant']:
                covered.add(info['consonant'])
            syllable_phonemes[syl] = covered

        # 优先级排序：半元音(0)、纯元音(1)、普通(2)
        def priority(syl):
            info = self.rules[syl]
            cons = info['consonant']
            if self.prioritize_semi_vowels and cons in self.semi_vowels:
                return 0
            if self.prioritize_vowel_transitions and not cons and info['transition']:
                return 1
            return 2

        # 贪心选择：每次选择能覆盖最多未覆盖目标音素的音节
        selected = []
        remaining = target_phonemes.copy()
        candidates = list(self.syllables)
        while remaining:
            best_syl = None
            best_covered = 0
            best_priority = 3
            for syl in candidates:
                if syl in selected:
                    continue
                covered = syllable_phonemes[syl] & remaining
                count = len(covered)
                if count == 0:
                    continue
                syl_priority = priority(syl)
                # 优先选择覆盖数量多的；若相同，优先级高者优先
                if (count > best_covered) or (count == best_covered and syl_priority < best_priority):
                    best_syl = syl
                    best_covered = count
                    best_priority = syl_priority
            if best_syl is None:
                # 理论上不会发生，但若发生则强制选一个
                best_syl = next((s for s in candidates if s not in selected), None)
                if best_syl is None:
                    break
            selected.append(best_syl)
            remaining -= syllable_phonemes[best_syl]

        return selected

    def _get_entry_aliases_for_protection(self, entry):
        """返回条目中所有可能产生别名的部分（开头、结尾、衔接）"""
        parts = entry.split('_')
        aliases = []
        for idx, alias in enumerate(parts):
            if alias == '-' or alias == 'R' or alias not in self.rules:
                continue
            info = self.rules[alias]
            # 开头别名
            if idx == 0 or (idx > 0 and parts[idx-1] == '-'):
                if self.first_sound == 'onset':
                    aliases.append(f"- {info['onset']}")
                elif self.first_sound == 'consonant':
                    cons = info['consonant']
                    aliases.append(f"- {cons}" if cons else f"- {info['onset']}")
            # 结尾别名
            if idx == len(parts)-1 or (idx < len(parts)-1 and parts[idx+1] == '-'):
                coda = info['coda']
                if coda:
                    aliases.append(f"{coda} {self.get_end_separator()}")
                else:
                    aliases.append(f"{info['onset']} {self.get_end_separator()}")
            # 衔接组合别名（简单起见，可以省略，但统计中不包含也不影响合并判断）
        return aliases

    def _get_covered_combinations(self, entries):
        covered = set()
        for entry in entries:
            parts = entry.split('_')
            for i in range(len(parts)-1):
                cur, nxt = parts[i], parts[i+1]
                if cur == '-' or nxt == '-':
                    continue
                if cur not in self.rules or nxt not in self.rules:
                    continue

                if self.mode == 'vccv-cvvc':
                    coda = self.rules[cur]['coda']
                    consonant = self.rules[nxt]['consonant']
                    if coda and consonant:
                        covered.add(('core', coda, consonant))
                    if self.ensure_vowel_link and not self.rules[nxt]['consonant']:
                        vowel_onset = self.rules[nxt]['onset']
                        if coda and vowel_onset:
                            covered.add(('vowel', coda, vowel_onset))
                elif self.mode == 'vcv':
                    coda = self.rules[cur]['coda']
                    onset = self.rules[nxt]['onset']
                    if coda and onset:
                        if self.rules[nxt]['consonant']:
                            covered.add(('core', coda, onset))
                        elif self.ensure_vowel_link:
                            covered.add(('vowel', coda, onset))
                elif self.mode == 'cvc':
                    onset = self.rules[cur]['onset']
                    consonant = self.rules[nxt]['consonant']
                    if onset and consonant:
                        covered.add(('core', onset, consonant))
                    if self.ensure_vowel_link and not self.rules[nxt]['consonant']:
                        vowel_onset = self.rules[nxt]['onset']
                        if onset and vowel_onset:
                            covered.add(('vowel', onset, vowel_onset))
        return covered

    def _get_all_needed_combinations(self):
        combos = set()
        if self.mode == 'vccv-cvvc':
            for coda in self.all_codas:
                for consonant in self.all_consonants:
                    combos.add(('core', coda, consonant))
                if self.ensure_vowel_link:
                    for vowel_onset in self.all_vowel_onsets:
                        combos.add(('vowel', coda, vowel_onset))
        elif self.mode == 'vcv':
            for coda in self.all_codas:
                for onset in self.all_onsets:
                    syl = next((s for s in self.syllables if self.rules[s]['onset'] == onset), None)
                    if syl and self.rules[syl]['consonant']:
                        combos.add(('core', coda, onset))
                    elif self.ensure_vowel_link:
                        combos.add(('vowel', coda, onset))
        elif self.mode == 'cvc':
            for onset in self.all_onsets:
                for consonant in self.all_consonants:
                    combos.add(('core', onset, consonant))
                if self.ensure_vowel_link:
                    for vowel_onset in self.all_vowel_onsets:
                        combos.add(('vowel', onset, vowel_onset))
        return combos

    def _get_left_phoneme(self, syl):
        if self.mode in ('vccv-cvvc', 'vcv'):
            return self.rules[syl]['coda']
        elif self.mode == 'cvc':
            return self.rules[syl]['onset']
        return None

    def _get_right_phoneme_for_combo(self, syl, combo_type):
        if combo_type == 'core':
            if self.mode == 'vccv-cvvc':
                return self.rules[syl]['consonant']
            elif self.mode == 'vcv':
                return self.rules[syl]['onset']
            elif self.mode == 'cvc':
                return self.rules[syl]['consonant']
        elif combo_type == 'vowel':
            return self.rules[syl]['onset']
        return None

    def _generate_standard(self, covered_combos, covered_syllables):
        def is_pure_vowel_onset(onset):
            for syl in self.syllables:
                if self.rules[syl]['onset'] == onset and not self.rules[syl]['consonant'] and self.rules[syl]['transition']:
                    return True
            return False
        
        def left_syl_sort_key(syl):
            # 左音节排序始终使用自然排序，不受优先级开关影响
            return natural_sort_key(syl)
                  
        entries = []

        if self.mode == 'cv':
            self.log(2, "CV 模式，无衔接部生成")
            return entries

        if self.first_sound != 'none' and self.ensure_all_syllables_standard:
            self.log(2, "当前策略：轮换左音节")
        else:
            self.log(2, "当前策略：固定左音节（保护关闭，允许省略完整发音）")

        needed = self._get_all_needed_combinations()
        remaining = needed - covered_combos
        self.log(2, f"需要覆盖组合总数: {len(needed)}，剩余: {len(remaining)}")

        left_to_rights = defaultdict(lambda: {'core': set(), 'vowel': set()})
        for combo in remaining:
            ctype, left, right = combo
            left_to_rights[left][ctype].add(right)

        # 每组右音节数量：使条目长度不超过 max_syllables
        max_right_per_group = max(1, self.max_syllables // 2)

        for left, rights_dict in left_to_rights.items():
            left_syl_index = 0
            right_syl_index = 0
            # 核心组合
            if rights_dict['core']:
                left_syls = [s for s in self.syllables if self._get_left_phoneme(s) == left]
                if left_syls:
                    left_syls.sort(key=left_syl_sort_key)
                    # 半元音优先排序（仅在标准保护关闭且开关开启时生效）
                    if self.prioritize_semi_vowels and not self.ensure_all_syllables_standard:
                        rights = sorted(
                            rights_dict['core'],
                            key=lambda r: (0 if r in self.semi_vowels else 1, natural_sort_key(r))
                        )
                    else:
                        rights = sorted(rights_dict['core'], key=natural_sort_key)
                    for i in range(0, len(rights), max_right_per_group):
                        group = rights[i:i+max_right_per_group]
                        seq = []
                        for r in group:
                            # 根据右音素找到右音节（完整发音）
                            right_candidates_all = [s for s in self.syllables if self._get_right_phoneme_for_combo(s, 'core') == r]
                            if not right_candidates_all:
                                continue
                            # ---- 连续重复排除：如果即将形成三个连续相同音节，排除该右音节 ----
                            if len(seq) >= 2 and seq[-1] == seq[-2]:
                                forbidden = seq[-1]
                            else:
                                forbidden = None
                            right_candidates = [s for s in right_candidates_all if s != forbidden]
                            if not right_candidates:
                                # 没有其他候选，则放弃该右音素
                                continue
                            # 贪心选择：优先选出现次数最少的音节
                            right_candidates.sort(key=lambda s: (self.syllable_usage_count.get(s, 0), natural_sort_key(s)))
                            right_syl = right_candidates[0]
                            self.syllable_usage_count[right_syl] = self.syllable_usage_count.get(right_syl, 0) + 1

                            # ---- 左音节选择（避免连续重复） ----
                            if len(seq) >= 2 and seq[-1] == seq[-2]:
                                # 前两个音节相同，排除与 seq[-1] 相同的左音节
                                left_candidates = [s for s in left_syls if s != seq[-1]]
                                if left_candidates:
                                    left_syl = left_candidates[left_syl_index % len(left_candidates)]
                                else:
                                    left_syl = left_syls[left_syl_index % len(left_syls)]  # 无候选时回退
                            else:
                                left_syl = left_syls[left_syl_index % len(left_syls)]

                            self.syllable_usage_count[left_syl] = self.syllable_usage_count.get(left_syl, 0) + 1
                            seq.append(left_syl)
                            seq.append(right_syl)
                            left_syl_index += 1
                        if seq:
                            # 如果长度小于最大音节数，追加一个左音节作为结尾（奇数最大音节数场景）
                            if len(seq) < self.max_syllables:
                                left_syl = left_syls[left_syl_index % len(left_syls)]
                                seq.append(left_syl)
                                left_syl_index += 1
                                self.syllable_usage_count[left_syl] = self.syllable_usage_count.get(left_syl, 0) + 1
                            entry = '_'.join(seq)
                            entries.append(entry)
                            for s in seq:
                                if s != 'R':
                                    covered_syllables.add(s)
                            self.log(2, f"生成条目: {entry}")

            # 元音链接
            if rights_dict['vowel'] and self.ensure_vowel_link:
                left_syls = [s for s in self.syllables if self._get_left_phoneme(s) == left]
                if left_syls:
                    left_syls.sort(key=left_syl_sort_key)
                    # 纯元音优先排序（仅在标准保护关闭且开关开启时生效）
                    if self.prioritize_vowel_transitions and not self.ensure_all_syllables_standard:
                        rights = sorted(
                            rights_dict['vowel'],
                            key=lambda r: (0 if is_pure_vowel_onset(r) else 1, natural_sort_key(r))
                        )
                    else:
                        rights = sorted(rights_dict['vowel'], key=natural_sort_key)
                    for i in range(0, len(rights), max_right_per_group):
                        group = rights[i:i+max_right_per_group]
                        seq = []
                        for r in group:
                            right_candidates_all = [s for s in self.syllables if self._get_right_phoneme_for_combo(s, 'vowel') == r and not self.rules[s]['consonant']]
                            if not right_candidates_all:
                                continue
                            # ---- 连续重复排除：如果即将形成三个连续相同音节，排除该右音节 ----
                            if len(seq) >= 2 and seq[-1] == seq[-2]:
                                forbidden = seq[-1]
                            else:
                                forbidden = None
                            right_candidates = [s for s in right_candidates_all if s != forbidden]
                            if not right_candidates:
                                continue
                            right_candidates.sort(key=lambda s: (self.syllable_usage_count.get(s, 0), natural_sort_key(s)))
                            right_syl = right_candidates[0]
                            self.syllable_usage_count[right_syl] = self.syllable_usage_count.get(right_syl, 0) + 1

                            # ---- 左音节选择（避免连续重复） ----
                            if len(seq) >= 2 and seq[-1] == seq[-2]:
                                left_candidates = [s for s in left_syls if s != seq[-1]]
                                if left_candidates:
                                    left_syl = left_candidates[left_syl_index % len(left_candidates)]
                                else:
                                    left_syl = left_syls[left_syl_index % len(left_syls)]
                            else:
                                left_syl = left_syls[left_syl_index % len(left_syls)]

                            self.syllable_usage_count[left_syl] = self.syllable_usage_count.get(left_syl, 0) + 1
                            seq.append(left_syl)
                            seq.append(right_syl)
                            left_syl_index += 1
                        if seq:
                            # 如果长度小于最大音节数，追加一个左音节作为结尾（奇数最大音节数场景）
                            if len(seq) < self.max_syllables:
                                left_syl = left_syls[left_syl_index % len(left_syls)]
                                seq.append(left_syl)
                                left_syl_index += 1
                                self.syllable_usage_count[left_syl] = self.syllable_usage_count.get(left_syl, 0) + 1
                            entry = '_'.join(seq)
                            entries.append(entry)
                            for s in seq:
                                if s != 'R':
                                    covered_syllables.add(s)
                            self.log(2, f"生成条目: {entry}")

        # 确保每个音节至少出现一次（VCCV 模式覆盖 transition）
        if self.mode == 'vccv-cvvc':
            # 收集缺失音节，按自然排序
            missing_syllables = [s for s in self.syllables if s not in covered_syllables]
            missing_syllables.sort(key=natural_sort_key)

            for syl in missing_syllables:
                placed = False
                # 尝试追加到已有未满条目末尾（使 syl 处于非开头位置）
                for i, entry in enumerate(entries):
                    parts = entry.split('_')
                    if len(parts) < self.max_syllables:
                        entries[i] = entry + '_' + syl
                        covered_syllables.add(syl)
                        placed = True
                        break
                if not placed:
                    # 创建两音节条目：找一个已存在的音节作为开头，syl 作为第二位
                    first_syl = None
                    for existing_syl in self.syllables:
                        if existing_syl != syl and existing_syl in covered_syllables:
                            first_syl = existing_syl
                            break
                    if first_syl:
                        new_entry = f"{first_syl}_{syl}"
                        entries.append(new_entry)
                        covered_syllables.add(syl)
                        covered_syllables.add(first_syl)
                    else:
                        # 极端情况：没有任何已有音节，则只能加单音节（此时 onset 可能缺失，但可接受）
                        entries.append(syl)
                        covered_syllables.add(syl)

        # 非 VCCV 强制覆盖衔接部音素
        if self.mode != 'vccv-cvvc' and self.transition_generation == 'all':
            transition_syls = [s for s in self.syllables if self.rules[s]['transition']]
            for syl in transition_syls:
                if syl not in covered_syllables:
                    placed = False
                    for i, entry in enumerate(entries):
                        parts = entry.split('_')
                        if len(parts) < self.max_syllables:
                            entries[i] = entry + '_' + syl
                            covered_syllables.add(syl)
                            placed = True
                            break
                    if not placed:
                        entries.append(syl)
                        covered_syllables.add(syl)

        return entries

    def _generate_missing_syllable_entries(self, covered_syllables):
        """
        找出所有未在录音表中出现的完整发音（音节），
        按最大音节数分组，每组音节用内部空拍 '-' 分隔生成独立条目。
        返回新增条目列表，并更新 covered_syllables。
        """
        present = set(covered_syllables)
        missing = [s for s in self.syllables if s not in present]
        if not missing:
            return []

        self.log(2, f"补全缺失完整发音: {missing}")
        missing.sort(key=natural_sort_key)

        new_entries = []
        group = []
        for syl in missing:
            if group:
                group.append('-')
            group.append(syl)
            # 关键修改：使用总元素数判断
            if len(group) >= self.max_syllables:
                entry = '_'.join(group).strip('-_')
                if entry:
                    new_entries.append(entry)
                    for s in group:
                        if s != '-':
                            covered_syllables.add(s)
                group = []
        if group:
            entry = '_'.join(group).strip('-_')
            if entry:
                new_entries.append(entry)
                for s in group:
                    if s != '-':
                        covered_syllables.add(s)
        
        return new_entries

    def _ensure_first_sound_coverage(self, entries):
        if self.first_sound == 'none':
            return entries

        # 收集已作为开头出现的音节
        covered_first_syllables = set()
        covered_first_phonemes = set()

        for entry in entries:
            parts = entry.split('_')
            for i, p in enumerate(parts):
                if p == '-':
                    continue
                if i == 0 or (i > 0 and parts[i-1] == '-'):
                    covered_first_syllables.add(p)
                    if p in self.rules:
                        if self.first_sound == 'onset':
                            covered_first_phonemes.add(self.rules[p]['onset'])
                        elif self.first_sound == 'consonant':
                            if self.rules[p]['consonant']:
                                covered_first_phonemes.add(self.rules[p]['consonant'])
                            # 纯元音忽略，不强制覆盖

        if self.first_sound == 'onset':
            # 找出所有未覆盖的 onset
            needed_onsets = set(self.rules[s]['onset'] for s in self.syllables)
            missing_onsets = needed_onsets - covered_first_phonemes
            # 选择每个缺失 onset 对应的音节
            missing_syllables = []
            for on in sorted(missing_onsets, key=natural_sort_key):
                syl = next((s for s in self.syllables if self.rules[s]['onset'] == on), None)
                if syl and syl not in covered_first_syllables:
                    missing_syllables.append(syl)
        elif self.first_sound == 'consonant':
            # 找出所有未覆盖的辅音
            needed_consonants = set(self.rules[s]['consonant'] for s in self.syllables if self.rules[s]['consonant'])
            missing_consonants = needed_consonants - covered_first_phonemes
            missing_syllables = []
            for cons in sorted(missing_consonants, key=natural_sort_key):
                syl = next((s for s in self.syllables if self.rules[s]['consonant'] == cons), None)
                if syl and syl not in covered_first_syllables:
                    missing_syllables.append(syl)

            # 同时确保纯元音（无辅音）的 onset 也被覆盖
            vowel_onsets_needed = set(self.rules[s]['onset'] for s in self.syllables if not self.rules[s]['consonant'])
            covered_vowel_onsets = set()
            for s in covered_first_syllables:
                if s in self.rules and not self.rules[s]['consonant']:
                    covered_vowel_onsets.add(self.rules[s]['onset'])
            missing_vowel_onsets = vowel_onsets_needed - covered_vowel_onsets
            for on in sorted(missing_vowel_onsets, key=natural_sort_key):
                syl = next((s for s in self.syllables if self.rules[s]['onset'] == on and not self.rules[s]['consonant']), None)
                if syl and syl not in covered_first_syllables:
                    missing_syllables.append(syl)
        else:
            return entries

        if not missing_syllables:
            return entries

        self.log(4, f"开头音补全缺失音节: {missing_syllables}")

        new_entries = []
        current = []
        for syl in missing_syllables:
            if current:
                current.append("-")
            current.append(syl)
            # 关键修改：使用总元素数（包括休止符）判断，而不是音节数
            if len(current) >= self.max_syllables:
                entry = '_'.join(current).strip('-_')
                if entry:
                    new_entries.append(entry)
                current = []
        if current:
            entry = '_'.join(current).strip('-_')
            if entry:
                new_entries.append(entry)

        # 确保新条目不以 '-' 开头或结尾
        cleaned_new_entries = [e.strip('-_') for e in new_entries if e.strip('-_')]
        return entries + cleaned_new_entries

    def _merge_entries(self, entries):
        """
        将短条目贪心合并为不超过最大音节数的长条目（全局贪心，每轮选择最佳配对）。
        优先合并短条目，合并选择只考虑长度，并保护每个 coda 至少有一个条目以它为结尾。
        entries: 待合并的条目列表（可能包含不同长度）
        """
        if len(entries) <= 1:
            return entries

        # 按音节数升序排序，短条目优先合并
        sorted_entries = sorted(
            entries,
            key=lambda e: (len(e.split('_')), natural_sort_key(e))
        )
        items = [e.split('_') for e in sorted_entries]
        used = [False] * len(items)

        def get_start_alias(parts):
            if not parts:
                return None
            first = parts[0]
            if first == 'R' or first == '-':
                return None
            if first in self.rules:
                if self.first_sound == 'onset':
                    return f"- {self.rules[first]['onset']}"
                elif self.first_sound == 'consonant':
                    cons = self.rules[first]['consonant']
                    return f"- {cons}" if cons else f"- {self.rules[first]['onset']}"
            return None

        def get_end_alias(parts):
            if not parts:
                return None
            last = parts[-1]
            if last == 'R' or last == '-':
                return None
            if last in self.rules:
                coda = self.rules[last]['coda']
                if coda:
                    return f"{coda} {self.get_end_separator()}"
                else:
                    return f"{self.rules[last]['onset']} {self.get_end_separator()}"
            return None

        def get_coda(parts):
            if not parts:
                return None
            last = parts[-1]
            if last in self.rules:
                return self.rules[last]['coda']
            return None

        def compute_alias_counts():
            counts = defaultdict(int)
            for idx, parts in enumerate(items):
                if used[idx]:
                    continue
                start = get_start_alias(parts)
                end = get_end_alias(parts)
                if start:
                    counts[start] += 1
                if end:
                    counts[end] += 1
            return counts

        def compute_coda_end_counts():
            counts = defaultdict(int)
            for idx, parts in enumerate(items):
                if used[idx]:
                    continue
                coda = get_coda(parts)
                if coda:
                    counts[coda] += 1
            return counts

        # 主循环：反复寻找最佳配对
        while True:
            alias_counts = compute_alias_counts()
            coda_end_counts = compute_coda_end_counts()
            best_pair = None
            best_combined = None
            best_len = -1
            best_original_len = float('inf')

            for i in range(len(items)):
                if used[i]:
                    continue
                for j in range(i+1, len(items)):
                    if used[j]:
                        continue
                    for first_idx, second_idx in [(i, j), (j, i)]:
                        first_parts = items[first_idx]
                        second_parts = items[second_idx]

                        start_second = get_start_alias(second_parts)
                        end_first = get_end_alias(first_parts)
                        unique_start_second = start_second and alias_counts.get(start_second, 0) == 1
                        unique_end_first = end_first and alias_counts.get(end_first, 0) == 1
                        need_protect = unique_start_second or unique_end_first

                        if need_protect:
                            if first_parts[-1] == second_parts[0]:
                                continue
                            combined = first_parts + ['R'] + second_parts
                        else:
                            if first_parts[-1] == second_parts[0]:
                                combined = first_parts + second_parts[1:]
                            else:
                                combined = first_parts + second_parts

                        if len(combined) > self.max_syllables:
                            continue

                        # 检查 coda 结尾唯一性
                        coda_first = get_coda(first_parts)
                        coda_second = get_coda(second_parts)
                        new_coda = get_coda(second_parts)
                        temp_counts = coda_end_counts.copy()
                        if coda_first:
                            temp_counts[coda_first] -= 1
                        if coda_second:
                            temp_counts[coda_second] -= 1
                        if new_coda:
                            temp_counts[new_coda] = temp_counts.get(new_coda, 0) + 1

                        coda_lost = False
                        for coda, cnt in coda_end_counts.items():
                            if cnt > 0 and temp_counts.get(coda, 0) <= 0:
                                coda_lost = True
                                break
                        if coda_lost:
                            continue

                        # 选择最优：合并后长度最接近 max，若相同则合并前总长度更短
                        merge_len = len(combined)
                        original_len = len(first_parts) + len(second_parts)
                        if (merge_len > best_len) or \
                           (merge_len == best_len and original_len < best_original_len):
                            best_pair = (first_idx, second_idx)
                            best_combined = combined
                            best_len = merge_len
                            best_original_len = original_len

            if best_pair is None:
                break

            first_idx, second_idx = best_pair
            items[first_idx] = best_combined
            used[second_idx] = True

        merged = ['_'.join(parts) for idx, parts in enumerate(items) if not used[idx]]
        return merged
    
    def _merge_adjacent_duplicates(self, entries):
        """
        合并相邻条目中首尾相同的音节，避免连续三次重复。
        仅针对标准条目，强制条目和开头音条目不参与。
        """
        if len(entries) <= 1:
            return entries

        # 按自然排序后合并（排序可能影响，但合并逻辑不依赖顺序，仅相邻）
        sorted_entries = sorted(entries, key=natural_sort_key)
        merged = []
        current_parts = None

        for entry in sorted_entries:
            parts = entry.split('_')
            if current_parts is None:
                current_parts = parts
                continue

            # 检查当前条目末尾与即将合并条目的开头是否相同
            if current_parts[-1] == parts[0]:
                # 合并：去掉重复的首音节
                combined = current_parts + parts[1:]
                if len(combined) <= self.max_syllables:
                    current_parts = combined
                    continue
                else:
                    # 长度超限，则先保存当前，再开始新条目
                    merged.append('_'.join(current_parts))
                    current_parts = parts
            else:
                merged.append('_'.join(current_parts))
                current_parts = parts

        if current_parts is not None:
            merged.append('_'.join(current_parts))

        return merged

# ===== oto 生成 =====
class OTOGenerator:
    def __init__(self, rules, settings, debug_log=None):
        self.rules = rules
        self.settings = settings
        self.mode = settings['mode']
        self.bpm = settings['bpm']
        self.leading_silence = settings['leading_silence']
        self.max_alternatives = settings['max_alternatives']
        self.first_sound = settings['first_sound']
        self.ensure_coda_r = settings['ensure_coda_r']
        self.generate_coda_consonant = settings['generate_coda_consonant']
        self.generate_coda_onset = settings['generate_coda_onset']
        self.generate_onset_consonant = settings['generate_onset_consonant']
        self.generate_onset = settings['generate_onset']
        self.separator_format = settings['separator_format']
        self.beat_ms = 60000 / self.bpm if self.bpm > 0 else 500
        self.alias_count = defaultdict(int)
        self.oto_entries = []
        self.covered_aliases = set()
        self.debug_log = debug_log if debug_log is not None else []
        self.report = []   # 存储每个条目的详细处理信息
        
    def get_end_separator(self):
        return 'R' if self.separator_format == 'R-dash' else '-'

    def convert_line_for_filename(self, line):
        if self.separator_format == 'R-dash':
            return line.replace('-', 'R')
        return line

    def generate(self, recording_list, protected_entries=None, protected_syllables=None, remove_redundant=True,unique_entry_strategy='replace', first_onset_as_normal=False):
        self.unique_entry_strategy = unique_entry_strategy
        self.first_onset_as_normal = first_onset_as_normal
        self.alias_count.clear()
        self.oto_entries.clear()
        self.covered_aliases.clear()
        self.report = []
        self.unused_protected_entries = []

        protected_entries = protected_entries or set()
        protected_syllables = protected_syllables or set()

        if not remove_redundant or self.max_alternatives > 1:
            for line in recording_list:
                self._generate_for_line(line, add_to_oto=True)
            return self.oto_entries, []

        new_recording = []
        removed = []
        for line in recording_list:
            if line in protected_entries or any(s in line.split('_') for s in protected_syllables):
                len_before = len(self.oto_entries)
                self._generate_for_line(line, add_to_oto=True)
                if len(self.oto_entries) == len_before:
                    # 没有生成任何 oto，尝试策略
                    if not self._try_generate_for_unique_entry(line):
                        # 保护失败：该条目将被剔除，记录到 removed 和 unused_protected_entries
                        self.unused_protected_entries.append(line)
                        removed.append(line)   # 追加到被剔除列表
                if line not in removed:
                    new_recording.append(line)
                self.report.append({
                    'entry': line,
                    'status': 'protected' if line not in removed else 'failed_protected',
                    'aliases': self._get_line_aliases(line),
                    'new_aliases': [],
                    'removed': line in removed
                })
                continue

            before_aliases = set(self.covered_aliases)
            temp_aliases = self._get_line_aliases(line)
            has_new = any(alias not in before_aliases for alias in temp_aliases)
            if has_new:
                new_recording.append(line)
                self._generate_for_line(line, add_to_oto=True)
                new_alias_list = [alias for alias in temp_aliases if alias not in before_aliases]
                self.report.append({
                    'entry': line,
                    'status': 'added',
                    'aliases': temp_aliases,
                    'new_aliases': new_alias_list,
                    'removed': False
                })
            else:
                removed.append(line)
                self.debug_log.append(f"[冗余剔除] 剔除条目: {line}，其所有别名已被覆盖")
                self.report.append({
                    'entry': line,
                    'status': 'removed',
                    'aliases': temp_aliases,
                    'new_aliases': [],
                    'removed': True
                })
        # 在 generate 方法的末尾，return 之前
        self.check_coverage()
        return self.oto_entries, removed

    def _try_generate_for_unique_entry(self, line):
        """尝试为受保护且无 oto 的条目生成至少一条 oto。返回是否成功。"""
        if self.unique_entry_strategy == 'replace':
            return self._replace_duplicate_oto(line)
        elif self.unique_entry_strategy == 'backup_alias':
            return self._backup_alias_oto(line)
        return False

    def _replace_duplicate_oto(self, line):
        """删除与当前条目基础别名重复的一条 oto，然后重新生成当前条目。"""
        line_aliases = self._get_line_aliases(line)
        if not line_aliases:
            return False
        # 找到第一个与当前条目基础别名重复的已有 oto 条目
        target_base_alias = line_aliases[0]
        for i, entry in enumerate(self.oto_entries):
            if entry['alias'].split('#')[0] == target_base_alias:
                # 删除该条目
                removed_entry = self.oto_entries.pop(i)
                # 更新 alias_count 和 covered_aliases
                self.alias_count[target_base_alias] -= 1
                self.covered_aliases.discard(target_base_alias)  # 可能还有其他条目使用，但暂时移除
                # 如果还有其他相同 base_alias 的条目，需恢复 covered_aliases？我们简单处理：重新扫描
                self._rebuild_coverage()
                # 重新尝试生成当前行
                self._generate_for_line(line, add_to_oto=True)
                return True
        return False

    def _rebuild_coverage(self):
        """重建 covered_aliases 从 oto_entries 中。"""
        self.covered_aliases = set()
        for entry in self.oto_entries:
            base = entry['alias'].split('#')[0]
            self.covered_aliases.add(base)

    def _backup_alias_oto(self, line):
        """尝试为条目生成后备别名，顺序：单独整音、字外衔接、transition。"""
        line_aliases = self._get_line_aliases(line)
        # 获取该条目所有音节信息，构建后备候选
        parts = line.split('_')
        # 优先选择第一个音节的 onset 作为后备
        if parts[0] in self.rules:
            onset = self.rules[parts[0]]['onset']
            if self.generate_onset or self.first_onset_as_normal:
                # 如果 generate_onset 为 False，仍可尝试
                pass
            if onset not in self.alias_count:
                # 直接生成一个 oto 条目
                self._generate_single_alias_oto(line, onset)
                return True
        # 再尝试字外衔接：尾音到辅音
        for i in range(len(parts)-1):
            if parts[i] in self.rules and parts[i+1] in self.rules:
                coda = self.rules[parts[i]]['coda']
                cons = self.rules[parts[i+1]]['consonant']
                if coda and cons:
                    alias = f"{coda} {cons}"
                    if alias not in self.alias_count:
                        self._generate_single_alias_oto(line, alias)
                        return True
        # 最后尝试 transition
        for part in parts:
            if part in self.rules:
                for trans in self.rules[part]['transition']:
                    if trans not in self.alias_count:
                        self._generate_single_alias_oto(line, trans)
                        return True
        return False

    def _generate_single_alias_oto(self, line, alias):
        """为指定条目生成单个别名的 oto 条目（无论是否重复）。"""
        parts = line.split('_')
        filename = f"{self.convert_line_for_filename(line)}.wav"
        total_duration = self.beat_ms * len(parts)
        current_time = self.leading_silence
        # 使用最后位置或其他合适位置，简化：放在第一个音节结束处
        offset = current_time
        final_alias = alias
        if alias in self.alias_count:
            count = self.alias_count[alias]
            final_alias = f"{alias}#{count}"
        self.alias_count[alias] += 1
        self.covered_aliases.add(alias)
        self.oto_entries.append({
            'filename': filename,
            'alias': final_alias,
            'offset': offset,
            'consonant': self.beat_ms * 0.4,
            'cutoff': -(total_duration - self.beat_ms),
            'preutterance': self.beat_ms * 0.2,
            'overlap': self.beat_ms * 0.1
        })

    def _get_line_aliases(self, line):
        aliases = []
        parts = line.split('_')
        for idx, alias in enumerate(parts):
            alias = alias.strip()
            if alias == '-' or alias not in self.rules:
                continue
            info = self.rules[alias]
            onset = info['onset']
            coda = info['coda']
            consonant = info['consonant']
            transitions = info['transition']

            if idx == 0 or (idx > 0 and parts[idx-1] == '-'):
                if self.first_sound == 'none':
                    aliases.append(onset)
                elif self.first_sound == 'onset':
                    aliases.append(f"- {onset}")
                elif self.first_sound == 'consonant':
                    if consonant:
                        aliases.append(f"- {consonant}")
                        if self.first_onset_as_normal:
                            aliases.append(onset)  # 将开头整音视为普通整音
                    else:
                        aliases.append(f"- {onset}")
            else:
                if self.generate_onset:
                    aliases.append(onset)

            if self.settings.get('transition_generation', 'all') == 'all':
                for trans in transitions:
                    aliases.append(trans)

            if idx < len(parts)-1 and parts[idx+1] != '-':
                next_alias = parts[idx+1]
                if next_alias in self.rules:
                    next_info = self.rules[next_alias]
                    next_consonant = next_info['consonant']
                    next_onset = next_info['onset']

                    base_transition = None
                    if self.mode == 'vccv-cvvc':
                        if coda and next_consonant:
                            base_transition = f"{coda} {next_consonant}"
                        elif self.settings.get('ensure_vowel_link', True) and coda and not next_consonant:
                            base_transition = f"{coda} {next_onset}"
                    elif self.mode == 'vcv':
                        if coda and next_onset:
                            base_transition = f"{coda} {next_onset}"
                    elif self.mode == 'cvc':
                        if onset and next_consonant:
                            base_transition = f"{onset} {next_consonant}"
                        elif self.settings.get('ensure_vowel_link', True) and onset and not next_consonant:
                            base_transition = f"{onset} {next_onset}"

                    if base_transition:
                        aliases.append(base_transition)

                    if self.generate_coda_consonant and coda and next_consonant:
                        extra = f"{coda} {next_consonant}"
                        if extra != base_transition:
                            aliases.append(extra)
                    if self.generate_coda_onset and coda and next_onset:
                        extra = f"{coda} {next_onset}"
                        if extra != base_transition:
                            aliases.append(extra)
                    if self.generate_onset_consonant and onset and next_consonant:
                        extra = f"{onset} {next_consonant}"
                        if extra != base_transition:
                            aliases.append(extra)

            if idx == len(parts)-1 or (idx < len(parts)-1 and parts[idx+1] == '-'):
                if self.ensure_coda_r:
                    if coda:
                        aliases.append(f"{coda} {self.get_end_separator()}")
                    else:
                        aliases.append(f"{onset} {self.get_end_separator()}")
        return aliases

    def _calculate_timing(self, alias_type, P_i, N_i, onset, coda, current_info, next_info=None):
        """
        根据别名类型计算 OTO 时间参数（绝对时间计算，写入时转换为相对偏移量）。
        返回字典或 None（若无法计算）
        """
        beat_ms = self.beat_ms

        # 辅助：获取当前整音的 A 规则参数（用于许多规则）
        def get_onset_params(syl_info, beat_pos):
            # 按照 A 规则计算单音节整音参数
            onset = syl_info['onset']
            coda = syl_info['coda']
            preutt_pos = beat_pos  # 预发声在拍点
            cutoff_pos = beat_pos + 0.75 * beat_ms  # 右边界在拍点后 75%
            cons_pos = preutt_pos + 0.15 * (cutoff_pos - preutt_pos)  # 固定部
            fixed_dur = cons_pos - preutt_pos
            offset_pos = preutt_pos - fixed_dur
            if offset_pos < 0:
                offset_pos = 0
            overlap_pos = offset_pos + 0.3 * (preutt_pos - offset_pos)
            return {
                'offset': offset_pos,
                'preutt': preutt_pos,
                'cons': cons_pos,
                'cutoff': cutoff_pos,
                'overlap': overlap_pos
            }

        # 获取当前整音参数（使用 current_info 和拍点 P_i）
        current_onset = get_onset_params(current_info, P_i)

        # 获取下一整音参数（如果存在且不是休止符，用于 D/E 规则）
        next_onset = None
        if next_info is not None:
            next_onset = get_onset_params(next_info, N_i)

        # 分支处理
        if alias_type == 'onset':  # A 规则：单独整音
            offset_pos = current_onset['offset']
            preutt_pos = current_onset['preutt']
            cons_pos = current_onset['cons']
            cutoff_pos = current_onset['cutoff']
            overlap_pos = current_onset['overlap']

        elif alias_type == 'initial_consonant':  # B 规则：开头辅音
            # 左边界 = 整音左边界
            offset_pos = current_onset['offset']
            # 右边界 = 整音预发声
            cutoff_pos = current_onset['preutt']
            # 预发声 = 左边界和右边界的中点
            preutt_pos = (offset_pos + cutoff_pos) / 2
            # 固定部 = 右边界和预发声的中点
            cons_pos = (cutoff_pos + preutt_pos) / 2
            # 重叠 = 左边界和预发声的中点
            overlap_pos = offset_pos + (preutt_pos - offset_pos) / 2

        elif alias_type == 'transition':  # C 规则：字内过渡音
            # 左边界 = 整音预发声
            offset_pos = current_onset['preutt']
            # 右边界 = 整音右边界
            cutoff_pos = current_onset['cutoff']
            # 预发声 = 左右边界中点
            preutt_pos = (offset_pos + cutoff_pos) / 2
            # 固定部 = 右边界与预发声的中点
            cons_pos = (cutoff_pos + preutt_pos) / 2
            # 重叠 = 左边界与预发声的中点
            overlap_pos = offset_pos + (preutt_pos - offset_pos) / 2

        elif alias_type in ('coda_consonant', 'coda_vowel', 'coda_R'):
            # D/E/G 规则：尾音到下一发音（辅音、元音或休止符）
            if alias_type == 'coda_R' or next_onset is None:
                # G 规则：虚拟下一拍
                virtual_info = current_info  # 使用当前信息作为虚拟下一音节的近似
                virtual_onset = get_onset_params(virtual_info, N_i)
                next_offset = virtual_onset['offset']
                next_preutt = virtual_onset['preutt']
            else:
                # D/E 规则：使用实际下一整音
                next_offset = next_onset['offset']
                next_preutt = next_onset['preutt']

            # 预发声 = 当前整音右边界
            preutt_pos = current_onset['cutoff']
            # 固定部 = 下一整音左边界
            cons_pos = next_offset
            # 左边界 = 2*预发声 - 固定部
            offset_pos = 2 * preutt_pos - cons_pos
            # 右边界 = 下一整音预发声
            cutoff_pos = next_preutt
            # 重叠 = 左边界与预发声前 30% 处
            overlap_pos = offset_pos + 0.3 * (preutt_pos - offset_pos)

        elif alias_type == 'onset_consonant':  # F 规则：整音到辅音
            # 预发声 = 当前拍点
            preutt_pos = P_i
            # 右边界 = 下一拍起点
            cutoff_pos = N_i
            # 固定部 = 预发声与右边界之间前 15% 处
            cons_pos = preutt_pos + 0.15 * (cutoff_pos - preutt_pos)
            fixed_dur = cons_pos - preutt_pos
            # 左边界 = 预发声提前固定部时长
            offset_pos = preutt_pos - fixed_dur
            if offset_pos < 0:
                offset_pos = 0
            # 重叠 = 预发声与左边界之间前 30% 处
            overlap_pos = offset_pos + 0.3 * (preutt_pos - offset_pos)

        else:
            return None

        # 转换为写入值（相对 offset 的偏移量）
        offset = int(round(offset_pos))
        consonant = int(round(cons_pos - offset_pos))  # 固定部 - 左边界 = 正值
        preutt = int(round(preutt_pos - offset_pos))   # 预发声 - 左边界 = 正值
        cutoff = int(round(offset_pos - cutoff_pos))   # 左边界 - 右边界 = 负值
        overlap = int(round(overlap_pos - offset_pos)) # 重叠 - 左边界 = 正值

        return {
            'offset': offset,
            'consonant': consonant,
            'preutterance': preutt,
            'cutoff': cutoff,
            'overlap': overlap
        }

    def _generate_for_line(self, line, add_to_oto=True, force_at_least_one=False):
        parts = line.split('_')
        filename = f"{self.convert_line_for_filename(line)}.wav"

        beat_start = [self.leading_silence + i * self.beat_ms for i in range(len(parts) + 1)]

        for idx, alias in enumerate(parts):
            alias = alias.strip()
            if alias == '-' or alias not in self.rules:
                continue

            info = self.rules[alias]
            onset = info['onset']
            coda = info['coda']
            consonant = info['consonant']
            transitions = info['transition']

            P_i = beat_start[idx]
            N_i = beat_start[idx + 1]

            is_first = (idx == 0) or (idx > 0 and parts[idx - 1] == '-')
            is_last = (idx == len(parts) - 1) or (idx < len(parts) - 1 and parts[idx + 1] == '-')

            alias_entries = []

            # 开头别名
            if is_first:
                if self.first_sound == 'none':
                    alias_entries.append((onset, 'onset'))
                elif self.first_sound == 'onset':
                    alias_entries.append((f"- {onset}", 'onset'))
                elif self.first_sound == 'consonant':
                    if consonant:
                        alias_entries.append((f"- {consonant}", 'initial_consonant'))
                        if self.first_onset_as_normal:
                            alias_entries.append((onset, 'onset'))
                    else:
                        alias_entries.append((f"- {onset}", 'onset'))
            else:
                if self.generate_onset:
                    alias_entries.append((onset, 'onset'))

            # 字内衔接
            if self.settings.get('transition_generation', 'all') == 'all':
                for trans in transitions:
                    alias_entries.append((trans, 'transition'))

            # 相邻音节衔接
            if idx < len(parts) - 1 and parts[idx + 1] != '-' and parts[idx + 1] in self.rules:
                next_info = self.rules[parts[idx + 1]]
                next_consonant = next_info['consonant']
                next_onset = next_info['onset']

                if self.mode == 'vccv-cvvc':
                    if coda and next_consonant:
                        alias_entries.append((f"{coda} {next_consonant}", 'coda_consonant'))
                    elif self.settings.get('ensure_vowel_link', True) and coda and not next_consonant:
                        alias_entries.append((f"{coda} {next_onset}", 'coda_vowel'))
                elif self.mode == 'vcv':
                    if coda and next_onset:
                        alias_entries.append((f"{coda} {next_onset}", 'coda_vowel'))
                elif self.mode == 'cvc':
                    if onset and next_consonant:
                        alias_entries.append((f"{onset} {next_consonant}", 'onset_consonant'))

                # 顺带生成
                if self.generate_coda_consonant and coda and next_consonant:
                    extra = f"{coda} {next_consonant}"
                    if extra not in [a[0] for a in alias_entries]:
                        alias_entries.append((extra, 'coda_consonant'))
                if self.generate_coda_onset and coda and next_onset:
                    extra = f"{coda} {next_onset}"
                    if extra not in [a[0] for a in alias_entries]:
                        alias_entries.append((extra, 'coda_vowel'))
                if self.generate_onset_consonant and onset and next_consonant:
                    extra = f"{onset} {next_consonant}"
                    if extra not in [a[0] for a in alias_entries]:
                        alias_entries.append((extra, 'onset_consonant'))

            # 结尾别名
            if is_last and self.ensure_coda_r:
                if coda:
                    alias_entries.append((f"{coda} {self.get_end_separator()}", 'coda_R'))
                else:
                    alias_entries.append((f"{onset} {self.get_end_separator()}", 'coda_R'))

            generated_any = False
            for alias_str, alias_type in alias_entries:
                next_info_for_calc = None
                if idx < len(parts) - 1 and parts[idx + 1] != '-' and parts[idx + 1] in self.rules:
                    next_info_for_calc = self.rules[parts[idx + 1]]
                params = self._calculate_timing(alias_type, P_i, N_i, onset, coda, info, next_info_for_calc)
                if params is None:
                    continue

                base_alias = alias_str
                count = self.alias_count[base_alias]
                if self.max_alternatives == 0:
                    if count > 0 and not (force_at_least_one and not generated_any):
                        continue
                    if count > 0:
                        final_alias = f"{base_alias}#{count}"
                    else:
                        final_alias = base_alias
                else:
                    if count >= self.max_alternatives:
                        continue
                    final_alias = base_alias if count == 0 else f"{base_alias}#{count}"
                self.alias_count[base_alias] += 1
                self.covered_aliases.add(base_alias)
                generated_any = True
                if add_to_oto:
                    self.oto_entries.append({
                        'filename': filename,
                        'alias': final_alias,
                        'offset': params['offset'],
                        'consonant': params['consonant'],
                        'cutoff': params['cutoff'],
                        'preutterance': params['preutterance'],
                        'overlap': params['overlap']
                    })

    def check_coverage(self):
        expected = set()

        # 1. 开头音别名
        if self.first_sound == 'onset':
            for syl, info in self.rules.items():
                expected.add(f"- {info['onset']}")
        elif self.first_sound == 'consonant':
            for syl, info in self.rules.items():
                if info['consonant']:
                    expected.add(f"- {info['consonant']}")
                else:
                    expected.add(f"- {info['onset']}")

        # 2. 结尾音别名
        if self.ensure_coda_r:
            for syl, info in self.rules.items():
                if info['coda']:
                    expected.add(f"{info['coda']} {self.get_end_separator()}")
                else:
                    expected.add(f"{info['onset']} {self.get_end_separator()}")

        # 3. 单独整音别名
        if self.generate_onset:
            for syl, info in self.rules.items():
                expected.add(info['onset'])

        # 4. 过渡音别名（transition 字段中的每个音素）
        if self.settings.get('transition_generation', 'all') == 'all':
            for syl, info in self.rules.items():
                for trans in info['transition']:
                    expected.add(trans)

        # 5. 核心衔接组合（仅以 VCCV-CVVC 为例）
        if self.mode == 'vccv-cvvc':
            all_codas = set(info['coda'] for info in self.rules.values())
            all_consonants = set(info['consonant'] for info in self.rules.values() if info['consonant'])
            for coda in all_codas:
                for cons in all_consonants:
                    expected.add(f"{coda} {cons}")
                if self.settings.get('ensure_vowel_link', True):
                    for vowel_syl, vowel_info in self.rules.items():
                        if not vowel_info['consonant']:
                            expected.add(f"{coda} {vowel_info['onset']}")

        # 收集实际覆盖的别名
        covered = self.covered_aliases
        missing = expected - covered

        if missing:
            self.debug_log.append(f"[覆盖检查] 预期别名总数: {len(expected)}")
            self.debug_log.append(f"[覆盖检查] 缺失别名数: {len(missing)}")
            self.debug_log.append(f"[覆盖检查] 缺失别名: {sorted(missing)}")
        else:
            self.debug_log.append("[覆盖检查] 所有预期别名均已覆盖")
        return missing

# ===== 验证与补全 =====
def validate_and_complete(rules, settings, recording_list, max_syllables, debug_log=None):
    if debug_log is None:
        debug_log = []
    mode = settings['mode']
    first_sound = settings['first_sound']
    ensure_coda_r = settings['ensure_coda_r']
    ensure_vowel_link = settings['ensure_vowel_link']

    if mode == 'cv':
        missing_syllables = set(rules.keys()) - set(recording_list)
        recording_list.extend(missing_syllables)
        return recording_list, list(missing_syllables), []

    covered_first_onsets = set()
    covered_first_consonants = set()
    covered_codas = set()
    covered_syllables = set()
    covered_combinations = set()

    for entry in recording_list:
        parts = entry.split('_')
        covered_syllables.update([p for p in parts if p != '-'])
        for i, p in enumerate(parts):
            if p == '-':
                continue
            if p in rules:
                if i == 0 or (i > 0 and parts[i-1] == '-'):
                    if rules[p]['consonant']:
                        covered_first_consonants.add(rules[p]['consonant'])
                    covered_first_onsets.add(rules[p]['onset'])
                if ensure_coda_r:
                    if i == len(parts)-1 or (i+1 < len(parts) and parts[i+1] == '-'):
                        if rules[p]['coda']:
                            covered_codas.add(rules[p]['coda'])
                        else:
                            covered_codas.add(rules[p]['onset'])
                if i < len(parts)-1 and parts[i+1] != '-' and parts[i+1] in rules:
                    next_info = rules[parts[i+1]]
                    if mode in ('vccv-cvvc'):
                        coda = rules[p]['coda']
                        consonant = next_info['consonant']
                        if coda and consonant:
                            covered_combinations.add(('core', coda, consonant))
                        if ensure_vowel_link and not next_info['consonant']:
                            vowel_onset = next_info['onset']
                            if coda and vowel_onset:
                                covered_combinations.add(('vowel', coda, vowel_onset))
                    elif mode == 'vcv':
                        coda = rules[p]['coda']
                        onset = next_info['onset']
                        if coda and onset:
                            if next_info['consonant']:
                                covered_combinations.add(('core', coda, onset))
                            elif ensure_vowel_link:
                                covered_combinations.add(('vowel', coda, onset))
                    elif mode == 'cvc':
                        onset = rules[p]['onset']
                        consonant = next_info['consonant']
                        if onset and consonant:
                            covered_combinations.add(('core', onset, consonant))
                        if ensure_vowel_link and not next_info['consonant']:
                            vowel_onset = next_info['onset']
                            if onset and vowel_onset:
                                covered_combinations.add(('vowel', onset, vowel_onset))

    needed_first_onsets = set(rules[s]['onset'] for s in rules)
    needed_first_consonants = set(rules[s]['consonant'] for s in rules if rules[s]['consonant'])
    needed_codas = set(rules[s]['coda'] for s in rules)

    needed_combinations = set()
    if mode in ('vccv-cvvc'):
        all_codas = needed_codas
        all_consonants = set(rules[s]['consonant'] for s in rules if rules[s]['consonant'])
        for c in all_codas:
            for cons in all_consonants:
                needed_combinations.add(('core', c, cons))
        if ensure_vowel_link:
            vowel_onsets = set(rules[s]['onset'] for s in rules if not rules[s]['consonant'])
            for c in all_codas:
                for vo in vowel_onsets:
                    needed_combinations.add(('vowel', c, vo))
    elif mode == 'vcv':
        all_codas = needed_codas
        all_onsets = needed_first_onsets
        for c in all_codas:
            for on in all_onsets:
                syl = next((s for s in rules if rules[s]['onset'] == on), None)
                if syl:
                    if rules[syl]['consonant']:
                        needed_combinations.add(('core', c, on))
                    elif ensure_vowel_link:
                        needed_combinations.add(('vowel', c, on))
    elif mode == 'cvc':
        all_onsets = needed_first_onsets
        all_consonants = set(rules[s]['consonant'] for s in rules if rules[s]['consonant'])
        for on in all_onsets:
            for cons in all_consonants:
                needed_combinations.add(('core', on, cons))
        if ensure_vowel_link:
            vowel_onsets = set(rules[s]['onset'] for s in rules if not rules[s]['consonant'])
            for on in all_onsets:
                for vo in vowel_onsets:
                    needed_combinations.add(('vowel', on, vo))

    missing = []
    if first_sound == 'onset':
        missing.extend(['-'+on for on in needed_first_onsets if on not in covered_first_onsets])
    elif first_sound == 'consonant':
        missing.extend(['-'+cons for cons in needed_first_consonants if cons not in covered_first_consonants])
        for syl in rules:
            if not rules[syl]['consonant']:
                on = rules[syl]['onset']
                if on not in covered_first_onsets:
                    missing.append('-'+on)

    if ensure_coda_r:
        missing.extend([c+' -' for c in needed_codas if c not in covered_codas])

    missing_combos = needed_combinations - covered_combinations
    added_entries = []
    if missing_combos:
        debug_log.append(f"[验证补全] 缺失组合数: {len(missing_combos)}")
        sample_combos = list(missing_combos)[:20]
        debug_log.append(f"[验证补全] 缺失组合示例: {sample_combos}")
        left_to_rights = defaultdict(lambda: {'core': set(), 'vowel': set()})
        for ctype, left, right in missing_combos:
            left_to_rights[left][ctype].add(right)

        for left, rights_dict in left_to_rights.items():
            left_syl_index = 0
            right_syl_index = 0
            if mode in ('vccv-cvvc', 'vcv'):
                left_syls = [s for s in rules if rules[s]['coda'] == left]
            else:
                left_syls = [s for s in rules if rules[s]['onset'] == left]

            debug_log.append(f"[验证补全] 左元素 '{left}' 缺失组合数: 核心 {len(rights_dict['core'])}, 元音 {len(rights_dict['vowel'])}")

            if not left_syls:
                continue
            left_syl = left_syls[0]

            if rights_dict['core']:
                right_syls = []
                for r in rights_dict['core']:
                    if mode == 'vccv-cvvc':
                        rs = next((s for s in rules if rules[s]['consonant'] == r), None)
                    elif mode == 'vcv':
                        rs = next((s for s in rules if rules[s]['onset'] == r and rules[s]['consonant']), None)
                    elif mode == 'cvc':
                        rs = next((s for s in rules if rules[s]['consonant'] == r), None)
                    if rs:
                        right_syls.append(rs)
                if right_syls:
                    right_syls.sort(key=natural_sort_key)
                    seq = []
                    for rs in right_syls:
                        seq.append(left_syl)
                        seq.append(rs)
                    segment = []
                    for syl in seq:
                        segment.append(syl)
                        if len(segment) == max_syllables:
                            entry = '_'.join(segment)
                            if entry not in recording_list and entry not in added_entries:
                                recording_list.append(entry)
                                added_entries.append(entry)
                                missing.append(entry)
                                debug_log.append(f"[验证补全] 补全条目: {entry}")
                            segment = []
                    if segment:
                        entry = '_'.join(segment)
                        if entry not in recording_list and entry not in added_entries:
                            recording_list.append(entry)
                            added_entries.append(entry)
                            missing.append(entry)
                            debug_log.append(f"[验证补全] 补全条目: {entry}")

            if rights_dict['vowel'] and ensure_vowel_link:
                right_syls = []
                for r in rights_dict['vowel']:
                    rs = next((s for s in rules if not rules[s]['consonant'] and rules[s]['onset'] == r), None)
                    if rs:
                        right_syls.append(rs)
                if right_syls:
                    right_syls.sort(key=natural_sort_key)
                    seq = []
                    for rs in right_syls:
                        seq.append(left_syl)
                        seq.append(rs)
                    segment = []
                    for syl in seq:
                        segment.append(syl)
                        if len(segment) == max_syllables:
                            entry = '_'.join(segment)
                            if entry not in recording_list and entry not in added_entries:
                                recording_list.append(entry)
                                added_entries.append(entry)
                                missing.append(entry)
                                debug_log.append(f"[验证补全] 补全条目: {entry}")
                            segment = []
                    if segment:
                        entry = '_'.join(segment)
                        if entry not in recording_list and entry not in added_entries:
                            recording_list.append(entry)
                            added_entries.append(entry)
                            missing.append(entry)
                            debug_log.append(f"[验证补全] 补全条目: {entry}")
    else:
        debug_log.append("[验证补全] 所有组合已覆盖，无需补全")

    if missing:
        return recording_list, missing, added_entries
    return recording_list, [], []

# ===== UI =====
class Application:
    def __init__(self, master):
        self.master = master
        master.title(get_text("title"))
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.8)
        master.geometry(f"{window_width}x{window_height}")
        master.minsize(900, 700)
        self.warning_shown_unused_unique = False
        self.settings = load_config_file(config_file)
        self.generate_coda_consonant_var = tk.BooleanVar(value=self.settings['generate_coda_consonant'])
        self.generate_coda_onset_var = tk.BooleanVar(value=self.settings['generate_coda_onset'])
        self.generate_onset_consonant_var = tk.BooleanVar(value=self.settings['generate_onset_consonant'])
        self.generate_onset_var = tk.BooleanVar(value=self.settings['generate_onset'])
        self.ensure_all_syllables_forced_var = tk.BooleanVar(value=self.settings['ensure_all_syllables_forced'])
        self.ensure_all_syllables_standard_var = tk.BooleanVar(value=self.settings['ensure_all_syllables_standard'])
        self.merge_short_entries_var = tk.BooleanVar(value=self.settings['merge_short_entries'])        
        self.oto_sort_var = tk.StringVar(value=self.settings['oto_sort'])
        self.unique_entry_strategy_var = tk.StringVar(value=self.settings.get('unique_entry_strategy', 'replace'))
        self.first_onset_as_normal_var = tk.BooleanVar(value=self.settings.get('first_onset_as_normal', False))
        self.redundancy_mode_var = tk.StringVar(value=self.settings.get('redundancy_mode', 'active_removal'))
        sort_mode = self.settings.get('global_sort_reclist', 'grouped')
        if sort_mode not in ('grouped', 'global'):
            sort_mode = 'grouped'
        display_sort = get_text("global_sort_grouped") if sort_mode == 'grouped' else get_text("global_sort_global")
        self.global_sort_reclist_var = tk.StringVar(value=display_sort)

        if self.settings['separator_format'] == 'R-dash':
            sep_display = get_text("separator_R_dash")
        else:
            sep_display = get_text("separator_dash_dash")
            
        self.separator_format_var = tk.StringVar(value=sep_display)
        self.enable_generate_extra_var = tk.BooleanVar(value=False)   # 默认关闭
        self.rules = {}
        self.recording_list = []
        self.oto_entries = []
        self.forced_set = set()
        self.first_sound_entries = set()
        self.warning_shown_first_sound = False
        self.warning_shown_coda_r = False
        self.warning_shown_vowel_link_off = False
        self.vccv_reminder_shown = False   # 是否已提醒过 VCCV 模式切换
        self.first_sound_internal = self.settings.get('first_sound', 'onset')
        self.generation_mode_internal = self.settings.get('generation_mode', 'none')
        self.debug_log = []

        self.transition_generation_var = tk.BooleanVar(value=(self.settings['transition_generation'] == 'all'))
        self.previous_mode = mode_var.get()   # 记录初始模式，用于模式切换提醒

        self.create_widgets()
        self.update_ui_from_settings()
        self.update_ui_text()

        self.unique_entry_strategy_label.config(text=get_text("unique_entry_strategy_label"))
        self.unique_entry_strategy_combo['values'] = [
            get_text("unique_entry_strategy_replace"),
            get_text("unique_entry_strategy_backup_alias")
        ]
        self.first_onset_as_normal_check.config(text=get_text("first_onset_as_normal_label"))
        self.redundancy_mode_label.config(text=get_text("redundancy_mode_label"))
        self.redundancy_mode_combo['values'] = [
            get_text("redundancy_mode_active_removal"),
            get_text("redundancy_mode_keep_all_syllables")
        ]
        self.global_sort_reclist_label.config(text=get_text("global_sort_reclist_label"))
        self.global_sort_reclist_combo['values'] = [
            get_text("global_sort_grouped"),
            get_text("global_sort_global")
        ]

    def update_onset_label(self):
        if mode_var.get() == 'vccv-cvvc':
            self.generate_onset_check.config(text=get_text("generate_onset_vccv_label"))
        else:
            self.generate_onset_check.config(text=get_text("generate_onset_label"))

    def validate_inputs(self):
        """验证输入值是否符合要求，失败则弹窗并返回 False。"""
        try:
            max_syl = int(self.max_syllables_entry.get())
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("error_max_syllables_int"))
            return False
        if max_syl < 1:
            messagebox.showerror(get_text("error"), get_text("error_max_syllables_min"))
            return False
        mode = mode_var.get()
        if mode in ('vccv-cvvc', 'vcv', 'cvc') and max_syl < 2:
            messagebox.showerror(get_text("error"), get_text("error_max_syllables_vccv_min"))
            return False

        try:
            leading = int(self.leading_silence_entry.get())
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("error_leading_silence_int"))
            return False
        if leading < 0:
            messagebox.showerror(get_text("error"), get_text("error_leading_silence_min"))
            return False

        try:
            max_alt = int(self.max_alternatives_entry.get())
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("error_max_alternatives_int"))
            return False
        if max_alt < 0:
            messagebox.showerror(get_text("error"), get_text("error_max_alternatives_min"))
            return False

        try:
            bpm = float(self.bpm_entry.get())
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("error_bpm_float"))
            return False
        if bpm <= 0:
            messagebox.showerror(get_text("error"), get_text("error_bpm_positive"))
            return False
        return True

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 规则文件选择
        rules_frame = ttk.Frame(main_frame)
        rules_frame.grid(row=0, column=0, sticky=tk.EW, pady=5)
        rules_frame.columnconfigure(1, weight=1)
        self.rules_file_label = ttk.Label(rules_frame, text=get_text("rules_file_label"))
        self.rules_file_label.grid(row=0, column=0, padx=5)
        self.rules_file_entry = ttk.Entry(rules_frame, textvariable=rules_file_path, state="readonly")
        self.rules_file_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.browse_button = ttk.Button(rules_frame, text=get_text("browse_button"), command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5)

        # 设置区
        settings_frame = ttk.LabelFrame(main_frame, text=get_text("settings_label"))
        settings_frame.grid(row=1, column=0, sticky=tk.EW, pady=5, padx=5)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)

        # 第一行：模式、最大音节数
        self.mode_label = ttk.Label(settings_frame, text=get_text("mode_label"))
        self.mode_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.mode_combobox = ttk.Combobox(settings_frame, textvariable=mode_var,
                                          values=["vccv-cvvc", "vcv", "cvc", "cv"],
                                          state="readonly", width=15)
        self.mode_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.mode_combobox.bind("<<ComboboxSelected>>", self.on_mode_changed)

        self.max_syllables_label = ttk.Label(settings_frame, text=get_text("max_syllables_label"))
        self.max_syllables_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.max_syllables_entry = ttk.Entry(settings_frame, width=10)
        self.max_syllables_entry.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=2)

        # 第二行：强制生成模式、BPM
        self.generation_mode_label = ttk.Label(settings_frame, text=get_text("generation_mode_label"))
        self.generation_mode_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.generation_mode_combobox = ttk.Combobox(
            settings_frame,
            textvariable=generation_mode_var,
            values=[
                get_text("generation_mode_none"),
                get_text("generation_mode_repeat"),
                get_text("generation_mode_interval"),
                get_text("generation_mode_sequence"),
            ],
            state="readonly",
            width=15
        )
        self.generation_mode_combobox.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.generation_mode_combobox.bind("<<ComboboxSelected>>", self.update_forced_check_visibility)
        self.generation_mode_combobox.bind("<<ComboboxSelected>>", self.on_generation_mode_changed)

        self.bpm_label = ttk.Label(settings_frame, text=get_text("bpm_label"))
        self.bpm_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.bpm_entry = ttk.Entry(settings_frame, width=10)
        self.bpm_entry.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=2)

        # 第三行：前导静音、最大后备条目名
        self.leading_silence_label = ttk.Label(settings_frame, text=get_text("leading_silence_label"))
        self.leading_silence_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.leading_silence_entry = ttk.Entry(settings_frame, width=10)
        self.leading_silence_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        self.max_alternatives_label = ttk.Label(settings_frame, text=get_text("max_alternatives_label"))
        self.max_alternatives_label.grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        self.max_alternatives_entry = ttk.Entry(settings_frame, width=10)
        self.max_alternatives_entry.grid(row=2, column=3, sticky=tk.EW, padx=5, pady=2)

        # 第四行：半元音列表、休止符格式
        self.semi_vowels_label = ttk.Label(settings_frame, text=get_text("semi_vowels_label"))
        self.semi_vowels_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.semi_vowels_entry = ttk.Entry(settings_frame, width=15)
        self.semi_vowels_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        self.separator_label = ttk.Label(settings_frame, text=get_text("separator_label"))
        self.separator_label.grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        self.separator_combobox = ttk.Combobox(settings_frame, textvariable=self.separator_format_var,
                                               values=[get_text("separator_R_dash"), get_text("separator_dash_dash")],
                                               state="readonly", width=18)
        self.separator_combobox.grid(row=3, column=3, sticky=tk.EW, padx=5, pady=2)

        # 第五行：开头音设置、衔接部产生
        self.first_sound_label = ttk.Label(settings_frame, text=get_text("first_sound_label"))
        self.first_sound_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.first_sound_combobox = ttk.Combobox(settings_frame, values=[
            get_text("first_sound_none"),
            get_text("first_sound_onset"),
            get_text("first_sound_consonant")
        ], state="readonly", width=18)

        self.first_sound_combobox.bind("<<ComboboxSelected>>", self.on_first_sound_changed)
        self.first_sound_combobox.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        self.transition_generation_label = ttk.Label(settings_frame, text=get_text("transition_generation_label"))
        self.transition_generation_label.grid(row=4, column=2, sticky=tk.W, padx=5, pady=2)
        self.transition_generation_check = ttk.Checkbutton(settings_frame,
                                                           text=get_text("transition_generation_all"),
                                                           variable=self.transition_generation_var)
        self.transition_generation_check.grid(row=4, column=3, sticky=tk.EW, padx=5, pady=2)

        # 保护组
        self.protect_frame = ttk.LabelFrame(settings_frame, text=get_text("protect_frame"))
        self.protect_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.protect_frame.columnconfigure(0, weight=1)

        self.ensure_all_syllables_forced_check = ttk.Checkbutton(self.protect_frame,
                                                                 text=get_text("ensure_all_syllables_forced_label"),
                                                                 variable=self.ensure_all_syllables_forced_var,
                                                                 command=self.update_protection_dependent_widgets)
        self.ensure_all_syllables_forced_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        self.ensure_all_syllables_standard_check = ttk.Checkbutton(self.protect_frame,
                                                                   text=get_text("ensure_all_syllables_standard_label"),
                                                                   variable=self.ensure_all_syllables_standard_var,
                                                                   command=self.update_protection_dependent_widgets)
        self.ensure_all_syllables_standard_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)

        self.ensure_coda_r_var = tk.BooleanVar(value=self.settings['ensure_coda_r'])
        self.ensure_coda_r_check = ttk.Checkbutton(self.protect_frame,
                                                   text=get_text("ensure_coda_r_label"),
                                                   variable=self.ensure_coda_r_var)
        self.ensure_coda_r_check.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)

        self.ensure_vowel_link_var = tk.BooleanVar(value=self.settings['ensure_vowel_link'])
        self.ensure_vowel_link_check = ttk.Checkbutton(self.protect_frame,
                                                       text=get_text("ensure_vowel_link_label"),
                                                       variable=self.ensure_vowel_link_var,
                                                       command=self.on_ensure_vowel_link_toggle)
        self.ensure_vowel_link_check.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)

        self.unique_entry_strategy_label = ttk.Label(self.protect_frame, text=get_text("unique_entry_strategy_label"))
        self.unique_entry_strategy_label.grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.unique_entry_strategy_combo = ttk.Combobox(
            self.protect_frame,
            textvariable=self.unique_entry_strategy_var,
            values=[get_text("unique_entry_strategy_replace"), get_text("unique_entry_strategy_backup_alias")],
            state="readonly", width=15
        )
        self.unique_entry_strategy_combo.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=2)

        # 优先级组
        self.priority_frame = ttk.LabelFrame(settings_frame, text=get_text("priority_frame"))
        self.priority_frame.grid(row=5, column=2, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        self.prioritize_semi_vowels_var = tk.BooleanVar(value=self.settings['prioritize_semi_vowels'])
        self.prioritize_semi_vowels_check = ttk.Checkbutton(self.priority_frame,
                                                            text=get_text("prioritize_semi_vowels_label"),
                                                            variable=self.prioritize_semi_vowels_var)
        self.prioritize_semi_vowels_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        self.prioritize_vowel_transitions_var = tk.BooleanVar(value=self.settings['prioritize_vowel_transitions'])
        self.prioritize_vowel_transitions_check = ttk.Checkbutton(self.priority_frame,
                                                                  text=get_text("prioritize_vowel_transitions_label"),
                                                                  variable=self.prioritize_vowel_transitions_var)
        self.prioritize_vowel_transitions_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)

        # 其他组
        self.other_frame = ttk.LabelFrame(settings_frame, text=get_text("other_frame"))
        self.other_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.other_frame.columnconfigure(1, weight=1)

        self.merge_short_entries_check = ttk.Checkbutton(self.other_frame,
                                                         text=get_text("merge_short_entries_label"),
                                                         variable=self.merge_short_entries_var)
        self.merge_short_entries_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        self.oto_sort_label = ttk.Label(self.other_frame, text=get_text("oto_sort_label"))
        self.oto_sort_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.oto_sort_combobox = ttk.Combobox(self.other_frame, textvariable=self.oto_sort_var,
                                              values=[get_text("oto_sort_order"), get_text("oto_sort_category")],
                                              state="readonly", width=15)
        self.oto_sort_combobox.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        self.redundancy_mode_label = ttk.Label(self.other_frame, text=get_text("redundancy_mode_label"))
        self.redundancy_mode_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.redundancy_mode_combo = ttk.Combobox(self.other_frame,
                                                  textvariable=self.redundancy_mode_var,
                                                  values=["active_removal", "keep_all_syllables"],
                                                  state="readonly", width=15)
        self.redundancy_mode_combo.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        self.global_sort_reclist_label = ttk.Label(self.other_frame, text=get_text("global_sort_reclist_label"))
        self.global_sort_reclist_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.global_sort_reclist_combo = ttk.Combobox(self.other_frame,
                                                      textvariable=self.global_sort_reclist_var,
                                                      values=[get_text("global_sort_grouped"), get_text("global_sort_global")],
                                                      state="readonly", width=15)
        self.global_sort_reclist_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        self.first_onset_as_normal_check = ttk.Checkbutton(self.other_frame,
                                                           text=get_text("first_onset_as_normal_label"),
                                                           variable=self.first_onset_as_normal_var)
        self.first_onset_as_normal_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        # 顺带生成组
        self.generate_frame = ttk.LabelFrame(settings_frame, text=get_text("generate_frame_label"))
        self.generate_frame.grid(row=6, column=2, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        self.enable_generate_extra_check = ttk.Checkbutton(
            self.generate_frame,
            text=get_text("enable_generate_extra"),
            variable=self.enable_generate_extra_var,
            command=self.update_generate_onset_state
        )
        self.enable_generate_extra_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        self.generate_coda_consonant_var = tk.BooleanVar(value=self.settings['generate_coda_consonant'])
        self.generate_coda_consonant_check = ttk.Checkbutton(self.generate_frame,
                                                             text=get_text("generate_coda_consonant_label"),
                                                             variable=self.generate_coda_consonant_var)
        self.generate_coda_consonant_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)

        self.generate_coda_onset_var = tk.BooleanVar(value=self.settings['generate_coda_onset'])
        self.generate_coda_onset_check = ttk.Checkbutton(self.generate_frame,
                                                         text=get_text("generate_coda_onset_label"),
                                                         variable=self.generate_coda_onset_var)
        self.generate_coda_onset_check.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)

        self.generate_onset_consonant_var = tk.BooleanVar(value=self.settings['generate_onset_consonant'])
        self.generate_onset_consonant_check = ttk.Checkbutton(self.generate_frame,
                                                              text=get_text("generate_onset_consonant_label"),
                                                              variable=self.generate_onset_consonant_var)
        self.generate_onset_consonant_check.grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)

        self.generate_onset_check = ttk.Checkbutton(self.generate_frame,
                                                    text=get_text("generate_onset_label"),
                                                    variable=self.generate_onset_var)
        self.generate_onset_check.grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)

        # 按钮行
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)

        self.load_config_button = ttk.Button(button_frame, text=get_text("load_config_button"), command=self.load_config)
        self.load_config_button.pack(side=tk.LEFT, padx=5)
        self.save_config_button = ttk.Button(button_frame, text=get_text("save_config_button"), command=self.save_config)
        self.save_config_button.pack(side=tk.LEFT, padx=5)
        self.generate_button = ttk.Button(button_frame, text=get_text("generate_button"), command=self.generate)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        self.export_reclist_button = ttk.Button(button_frame, text=get_text("export_reclist_button"),
                                                command=self.export_reclist, state="disabled")
        self.export_reclist_button.pack(side=tk.LEFT, padx=5)
        self.export_oto_button = ttk.Button(button_frame, text=get_text("export_oto_button"),
                                            command=self.export_oto, state="disabled")
        self.export_oto_button.pack(side=tk.LEFT, padx=5)

        # 语言选择
        lang_frame = ttk.Frame(button_frame)
        lang_frame.pack(side=tk.RIGHT, padx=5)
        self.language_label = ttk.Label(lang_frame, text=get_text("language_label"))
        self.language_label.pack(side=tk.LEFT)
        self.language_combobox = ttk.Combobox(lang_frame, textvariable=language_var,
                                              values=available_languages, state="readonly", width=5)
        self.language_combobox.pack(side=tk.LEFT, padx=5)
        self.language_combobox.bind("<<ComboboxSelected>>", self.switch_language)

        # 主内容区
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=3, column=0, sticky=tk.NSEW, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky=tk.NSEW)

        # 录音表 tab
        reclist_frame = ttk.Frame(self.notebook)
        reclist_frame.grid_rowconfigure(0, weight=1)
        reclist_frame.grid_columnconfigure(0, weight=1)
        self.result_text = tk.Text(reclist_frame, wrap="none", state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        reclist_scrollbar = ttk.Scrollbar(reclist_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        reclist_scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.config(yscrollcommand=reclist_scrollbar.set)
        reclist_copy_button = ttk.Button(reclist_frame, text=get_text("copy_all"),
                                         command=lambda: self.copy_to_clipboard(self.result_text))
        reclist_copy_button.grid(row=1, column=0, columnspan=2, sticky=tk.E, padx=5, pady=2)
        self.notebook.add(reclist_frame, text=get_text("recording_list"))

        # oto tab
        oto_frame = ttk.Frame(self.notebook)
        oto_frame.grid_rowconfigure(0, weight=1)
        oto_frame.grid_columnconfigure(0, weight=1)
        self.oto_text = tk.Text(oto_frame, wrap="none", state=tk.DISABLED)
        self.oto_text.grid(row=0, column=0, sticky="nsew")
        oto_scrollbar = ttk.Scrollbar(oto_frame, orient=tk.VERTICAL, command=self.oto_text.yview)
        oto_scrollbar.grid(row=0, column=1, sticky="ns")
        self.oto_text.config(yscrollcommand=oto_scrollbar.set)
        oto_copy_button = ttk.Button(oto_frame, text=get_text("copy_all"),
                                     command=lambda: self.copy_to_clipboard(self.oto_text))
        oto_copy_button.grid(row=1, column=0, columnspan=2, sticky=tk.E, padx=5, pady=2)
        self.notebook.add(oto_frame, text=get_text("oto_configuration"))

        # 被剔除条目 tab
        removed_frame = ttk.Frame(self.notebook)
        removed_frame.grid_rowconfigure(1, weight=1)
        removed_frame.grid_columnconfigure(0, weight=1)

        self.removed_count_label = ttk.Label(removed_frame, text=get_text("removed_count").format(0))
        self.removed_count_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

        self.removed_text = tk.Text(removed_frame, wrap="none", state=tk.DISABLED)
        self.removed_text.grid(row=1, column=0, sticky="nsew")
        removed_scrollbar = ttk.Scrollbar(removed_frame, orient=tk.VERTICAL, command=self.removed_text.yview)
        removed_scrollbar.grid(row=1, column=1, sticky="ns")
        self.removed_text.config(yscrollcommand=removed_scrollbar.set)

        removed_copy_button = ttk.Button(removed_frame, text=get_text("copy_all"),
                                         command=lambda: self.copy_to_clipboard(self.removed_text))
        removed_copy_button.grid(row=2, column=0, columnspan=2, sticky=tk.E, padx=5, pady=2)
        self.notebook.add(removed_frame, text=get_text("removed_title"))

        # 未使用的完整发音 tab
        unused_frame = ttk.Frame(self.notebook)
        unused_frame.grid_rowconfigure(0, weight=1)
        unused_frame.grid_columnconfigure(0, weight=1)
        self.unused_text = tk.Text(unused_frame, wrap="none", state=tk.DISABLED)
        self.unused_text.grid(row=0, column=0, sticky="nsew")
        unused_scrollbar = ttk.Scrollbar(unused_frame, orient=tk.VERTICAL, command=self.unused_text.yview)
        unused_scrollbar.grid(row=0, column=1, sticky="ns")
        self.unused_text.config(yscrollcommand=unused_scrollbar.set)
        unused_copy_button = ttk.Button(unused_frame, text=get_text("copy_all"),
                                        command=lambda: self.copy_to_clipboard(self.unused_text))
        unused_copy_button.grid(row=1, column=0, columnspan=2, sticky=tk.E, padx=5, pady=2)
        self.notebook.add(unused_frame, text=get_text("unused_syllables_title"))

        # 诊断 tab
        debug_frame = ttk.Frame(self.notebook)
        debug_frame.grid_rowconfigure(0, weight=1)
        debug_frame.grid_columnconfigure(0, weight=1)
        self.debug_text = tk.Text(debug_frame, wrap="none", state=tk.DISABLED)
        self.debug_text.grid(row=0, column=0, sticky="nsew")
        debug_scrollbar = ttk.Scrollbar(debug_frame, orient=tk.VERTICAL, command=self.debug_text.yview)
        debug_scrollbar.grid(row=0, column=1, sticky="ns")
        self.debug_text.config(yscrollcommand=debug_scrollbar.set)
        debug_copy_button = ttk.Button(debug_frame, text=get_text("copy_all"),
                                       command=lambda: self.copy_to_clipboard(self.debug_text))
        debug_copy_button.grid(row=1, column=0, columnspan=2, sticky=tk.E, padx=5, pady=2)
        self.notebook.add(debug_frame, text=get_text("debug_title"))

        # 状态栏
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.grid(row=4, column=0, sticky=tk.EW, pady=5)
        self.reclist_line_count_label = ttk.Label(self.status_frame, text=get_text("line_count_reclist").format(0))
        self.reclist_line_count_label.pack(side=tk.LEFT, padx=5)
        self.oto_line_count_label = ttk.Label(self.status_frame, text=get_text("line_count_oto").format(0))
        self.oto_line_count_label.pack(side=tk.LEFT, padx=20)
        self.status_warning_label = ttk.Label(self.status_frame, text="", foreground="orange")
        self.status_warning_label.pack(side=tk.LEFT, padx=20)
        self.update_first_onset_check_state()
        self.update_protection_dependent_widgets()
        self.update_generate_onset_state()
        self.update_forced_check_visibility()

    def on_mode_changed(self, event=None):
        new_mode = mode_var.get()
        old_mode = self.previous_mode
        self.previous_mode = new_mode
        self.update_generate_onset_state()
        self.update_cv_mode_ui()   # 新增：处理 CV 模式特殊 UI
        self.update_onset_label()
        if not self.vccv_reminder_shown:
            if old_mode != new_mode and (old_mode == 'vccv-cvvc' or new_mode == 'vccv-cvvc'):
                messagebox.showinfo(
                    get_text("transition_mode_reminder_title"),
                    get_text("transition_mode_reminder_text")
                )
                self.vccv_reminder_shown = True

    def update_first_onset_check_state(self):
        """根据 first_sound 内部值控制复选框状态"""
        if self.first_sound_internal == 'consonant':
            self.first_onset_as_normal_check.config(state=tk.NORMAL)
        else:
            self.first_onset_as_normal_var.set(False)
            self.first_onset_as_normal_check.config(state=tk.DISABLED)

    def on_first_sound_changed(self, event=None):
        """当开头音下拉框改变时，同步内部变量并刷新复选框状态"""
        display = self.first_sound_combobox.get()
        if display == get_text("first_sound_none"):
            self.first_sound_internal = 'none'
        elif display == get_text("first_sound_consonant"):
            self.first_sound_internal = 'consonant'
        else:
            self.first_sound_internal = 'onset'
        self.update_first_onset_check_state()

    def _generation_mode_to_display(self, internal):
        mapping = {
            'none': get_text("generation_mode_none"),
            'repeat': get_text("generation_mode_repeat"),
            'interval': get_text("generation_mode_interval"),
            'sequence': get_text("generation_mode_sequence"),
        }
        return mapping.get(internal, internal)

    def on_generation_mode_changed(self, event=None):
        """当强制生成模式下拉框改变时，同步内部变量并更新相关控件状态"""
        display = generation_mode_var.get()
        self.generation_mode_internal = self._generation_mode_to_internal(display)
        self.update_forced_check_visibility()

    def _generation_mode_to_internal(self, display):
        reverse = {
            get_text("generation_mode_none"): 'none',
            get_text("generation_mode_repeat"): 'repeat',
            get_text("generation_mode_interval"): 'interval',
            get_text("generation_mode_sequence"): 'sequence',
        }
        return reverse.get(display, display)

    def _unique_strategy_to_display(self, internal):
        mapping = {
            'replace': get_text("unique_entry_strategy_replace"),
            'backup_alias': get_text("unique_entry_strategy_backup_alias")
        }
        return mapping.get(internal, internal)

    def _unique_strategy_to_internal(self, display):
        reverse = {
            get_text("unique_entry_strategy_replace"): 'replace',
            get_text("unique_entry_strategy_backup_alias"): 'backup_alias'
        }
        return reverse.get(display, display)

    def _redundancy_mode_to_display(self, internal):
        mapping = {
            'active_removal': get_text("redundancy_mode_active_removal"),
            'keep_all_syllables': get_text("redundancy_mode_keep_all_syllables")
        }
        return mapping.get(internal, internal)

    def _redundancy_mode_to_internal(self, display):
        reverse = {
            get_text("redundancy_mode_active_removal"): 'active_removal',
            get_text("redundancy_mode_keep_all_syllables"): 'keep_all_syllables'
        }
        return reverse.get(display, display)

    def update_generate_onset_state(self, event=None):
        mode = mode_var.get()
        # 处理 generate_onset（特殊逻辑：CV 和 VCCV-CVVC 模式）
        if mode == 'cv':
            # CV 模式必须生成单独整音，强制勾选并禁用
            self.generate_onset_var.set(True)
            self.generate_onset_check.config(state=tk.DISABLED)
        elif mode == 'vccv-cvvc':
            # VCCV-CVVC 模式下，若“顺带生成”关闭，则禁用且不勾选
            if not self.enable_generate_extra_var.get():
                self.generate_onset_var.set(False)
                self.generate_onset_check.config(state=tk.DISABLED)
            else:
                # 启用顺带生成后，允许手动勾选，默认不勾选
                self.generate_onset_check.config(state=tk.NORMAL)
                # 若用户之前已勾选则保留，否则保持 False
        else:
            # 其他模式：受“顺带生成”开关控制
            if not self.enable_generate_extra_var.get():
                self.generate_onset_var.set(False)
                self.generate_onset_check.config(state=tk.DISABLED)
            else:
                self.generate_onset_check.config(state=tk.NORMAL)

        # 处理其他顺带生成项（受总开关影响）
        if not self.enable_generate_extra_var.get():
            self.generate_coda_consonant_var.set(False)
            self.generate_coda_onset_var.set(False)
            self.generate_onset_consonant_var.set(False)
            self.generate_coda_consonant_check.config(state=tk.DISABLED)
            self.generate_coda_onset_check.config(state=tk.DISABLED)
            self.generate_onset_consonant_check.config(state=tk.DISABLED)
        else:
            self.generate_coda_consonant_check.config(state=tk.NORMAL)
            self.generate_coda_onset_check.config(state=tk.NORMAL)
            self.generate_onset_consonant_check.config(state=tk.NORMAL)

            # 根据模式自动勾选并禁用必需项（仅限顺带生成中的必需项）
            if mode == 'vccv-cvvc':
                self.generate_coda_consonant_var.set(True)
                self.generate_coda_consonant_check.config(state=tk.DISABLED)
            else:
                self.generate_coda_consonant_check.config(state=tk.NORMAL)

            if mode == 'vcv':
                self.generate_coda_onset_var.set(True)
                self.generate_coda_onset_check.config(state=tk.DISABLED)
            else:
                self.generate_coda_onset_check.config(state=tk.NORMAL)

            if mode == 'cvc':
                self.generate_onset_consonant_var.set(True)
                self.generate_onset_consonant_check.config(state=tk.DISABLED)
            else:
                self.generate_onset_consonant_check.config(state=tk.NORMAL)

    def on_ensure_vowel_link_toggle(self):
        """当用户切换“确保纯元音链接”时，若在 VCCV-CVVC 模式且取消勾选，则自动勾选“单独整音（纯元音）”并警告一次。"""
        if mode_var.get() != 'vccv-cvvc':
            return
        if not self.ensure_vowel_link_var.get():
            # 用户取消了纯元音链接，自动勾选单独整音（纯元音）并警告
            if not self.generate_onset_var.get():
                self.generate_onset_var.set(True)
            if not getattr(self, 'warning_shown_vowel_link_off', False):
                self.warning_shown_vowel_link_off = True
                messagebox.showwarning(
                    get_text("warning"),
                    get_text("warning_vowel_link_off")
                )

    def update_protection_dependent_widgets(self):
        forced = self.ensure_all_syllables_forced_var.get()
        standard = self.ensure_all_syllables_standard_var.get()
        protect_on = forced or standard
        if protect_on:
            self.unique_entry_strategy_combo.config(state="readonly")
            self.redundancy_mode_combo.config(state="disabled")
        else:
            self.unique_entry_strategy_combo.config(state="disabled")
            self.redundancy_mode_combo.config(state="readonly")

    def update_forced_check_visibility(self, event=None):
        if self.generation_mode_internal == 'none':
            self.ensure_all_syllables_forced_check.config(state=tk.DISABLED)
            self.ensure_all_syllables_forced_var.set(False)   # 禁用时取消勾选
        else:
            self.ensure_all_syllables_forced_check.config(state=tk.NORMAL)
            # 保持 False，除非用户手动勾选；不自动恢复 True
        self.update_protection_dependent_widgets()

    def update_cv_mode_ui(self, event=None):
        """根据是否为 CV 模式调整界面控件状态和强制生成选项。"""
        mode = mode_var.get()
        if mode == 'cv':
            self.ensure_all_syllables_forced_var.set(True)
            self.ensure_all_syllables_forced_check.config(state=tk.DISABLED)
            # 强制生成不允许 none，若当前为 none 则改为 sequence
            if self.generation_mode_internal == 'none':
                self.generation_mode_internal = 'sequence'
                generation_mode_var.set(self._generation_mode_to_display('sequence'))
            self.generation_mode_combobox['values'] = [
                get_text("generation_mode_repeat"),
                get_text("generation_mode_interval"),
                get_text("generation_mode_sequence"),
            ]
            self.ensure_all_syllables_standard_check.config(state=tk.DISABLED)
            self.ensure_all_syllables_standard_var.set(False)
            self.ensure_vowel_link_check.config(state=tk.DISABLED)
            self.ensure_vowel_link_var.set(False)
        else:
            self.generation_mode_combobox['values'] = [
                get_text("generation_mode_none"),
                get_text("generation_mode_repeat"),
                get_text("generation_mode_interval"),
                get_text("generation_mode_sequence"),
            ]
            self.ensure_all_syllables_standard_check.config(state=tk.NORMAL)
            self.ensure_vowel_link_check.config(state=tk.NORMAL)
            self.ensure_all_syllables_forced_check.config(state=tk.NORMAL)
        self.update_forced_check_visibility()
        self.update_protection_dependent_widgets()


    def copy_to_clipboard(self, text_widget):
        content = text_widget.get("1.0", tk.END).strip()
        self.master.clipboard_clear()
        self.master.clipboard_append(content)
        self.status_warning_label.config(text=get_text("copied_to_clipboard"), foreground="green")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title=get_text("select_rule_file_title"),
            filetypes=(("INI files", "*.ini"), ("All files", "*.*"))
        )
        if filename:
            rules_file_path.set(filename)

    def load_config(self):
        filename = filedialog.askopenfilename(
            title=get_text("select_config_file_title"),
            filetypes=(("INI files", "*.ini"), ("All files", "*.*"))
        )
        if filename:
            self.settings = load_config_file(filename)
            self.update_ui_from_settings()

    def save_config(self):
        filename = filedialog.asksaveasfilename(
            title=get_text("save_config_file_title"),
            defaultextension=".ini",
            filetypes=(("INI files", "*.ini"), ("All files", "*.*"))
        )
        if filename:
            if not self.validate_inputs():
                return
            self.update_settings_from_ui()
            try:
                save_config_file(filename, self.settings)
                messagebox.showinfo(get_text("success"), get_text("config_saved").format(filename))
            except Exception as e:
                messagebox.showerror(get_text("error"), get_text("config_save_failed").format(e))

    def update_settings_from_ui(self):
        try:
            self.settings['max_syllables_per_sentence'] = int(self.max_syllables_entry.get())
        except:
            self.settings['max_syllables_per_sentence'] = 8
        self.settings['mode'] = mode_var.get()
        self.generation_mode_internal = self._generation_mode_to_internal(generation_mode_var.get())
        self.settings['generation_mode'] = self.generation_mode_internal
        try:
            self.settings['bpm'] = int(self.bpm_entry.get())
        except:
            self.settings['bpm'] = 120
        try:
            self.settings['leading_silence'] = int(self.leading_silence_entry.get())
        except:
            self.settings['leading_silence'] = 100
        try:
            self.settings['max_alternatives'] = int(self.max_alternatives_entry.get())
        except:
            self.settings['max_alternatives'] = 0
        self.settings['ensure_all_syllables_forced'] = self.ensure_all_syllables_forced_var.get()
        self.settings['ensure_all_syllables_standard'] = self.ensure_all_syllables_standard_var.get()
        self.settings['merge_short_entries'] = self.merge_short_entries_var.get()
        self.settings['unique_entry_strategy'] = self._unique_strategy_to_internal(self.unique_entry_strategy_var.get())
        self.settings['first_onset_as_normal'] = self.first_onset_as_normal_var.get()
        self.settings['redundancy_mode'] = self._redundancy_mode_to_internal(self.redundancy_mode_var.get())
        display_sort = self.global_sort_reclist_var.get()
        if display_sort == get_text("global_sort_grouped"):
            self.settings['global_sort_reclist'] = 'grouped'
        else:
            self.settings['global_sort_reclist'] = 'global'
        separator_display = self.separator_format_var.get()

        if separator_display == get_text("separator_R_dash"):
            self.settings['separator_format'] = 'R-dash'
        elif separator_display == get_text("separator_dash_dash"):
            self.settings['separator_format'] = 'dash-dash'
        else:
            # 兼容旧配置或意外情况
            self.settings['separator_format'] = 'R-dash' if 'R' in str(separator_display) else 'dash-dash'
        if self.oto_sort_var.get() == get_text("oto_sort_order"):
            self.settings['oto_sort'] = 'order'
        else:
            self.settings['oto_sort'] = 'category'
        self.settings['prioritize_semi_vowels'] = self.prioritize_semi_vowels_var.get()
        self.settings['prioritize_vowel_transitions'] = self.prioritize_vowel_transitions_var.get()
        self.settings['ensure_coda_r'] = self.ensure_coda_r_var.get()
        self.settings['ensure_vowel_link'] = self.ensure_vowel_link_var.get()
        self.settings['semi_vowels'] = self.semi_vowels_entry.get().strip()
        first_sound_text = self.first_sound_combobox.get()
        if first_sound_text == get_text("first_sound_none"):
            self.settings['first_sound'] = 'none'
            self.first_sound_internal = 'none'
        elif first_sound_text == get_text("first_sound_consonant"):
            self.settings['first_sound'] = 'consonant'
            self.first_sound_internal = 'consonant'
        else:
            self.settings['first_sound'] = 'onset'
            self.first_sound_internal = 'onset'
        if self.transition_generation_var.get():
            self.settings['transition_generation'] = 'all'
        else:
            self.settings['transition_generation'] = 'none'

        # 处理 generate_onset：模式必需项优先
        if self.settings['mode'] in ('cv', 'vccv-cvvc'):
            self.settings['generate_onset'] = True
        else:
            if self.enable_generate_extra_var.get():
                self.settings['generate_onset'] = self.generate_onset_var.get()
            else:
                self.settings['generate_onset'] = False

        # 处理其他顺带生成项
        if self.enable_generate_extra_var.get():
            self.settings['generate_coda_consonant'] = self.generate_coda_consonant_var.get()
            self.settings['generate_coda_onset'] = self.generate_coda_onset_var.get()
            self.settings['generate_onset_consonant'] = self.generate_onset_consonant_var.get()
        else:
            self.settings['generate_coda_consonant'] = False
            self.settings['generate_coda_onset'] = False
            self.settings['generate_onset_consonant'] = False

    def update_ui_from_settings(self):
        self.max_syllables_entry.delete(0, tk.END)
        self.max_syllables_entry.insert(0, str(self.settings['max_syllables_per_sentence']))
        mode_var.set(self.settings['mode'])
        gen_mode_internal = self.settings.get('generation_mode', 'none')
        generation_mode_var.set(self._generation_mode_to_display(gen_mode_internal))
        self.generation_mode_internal = gen_mode_internal
        self.bpm_entry.delete(0, tk.END)
        self.bpm_entry.insert(0, str(self.settings['bpm']))
        self.leading_silence_entry.delete(0, tk.END)
        self.leading_silence_entry.insert(0, str(self.settings['leading_silence']))
        self.max_alternatives_entry.delete(0, tk.END)
        self.max_alternatives_entry.insert(0, str(self.settings['max_alternatives']))
        self.semi_vowels_entry.delete(0, tk.END)
        self.semi_vowels_entry.insert(0, self.settings['semi_vowels'])
        self.ensure_all_syllables_forced_var.set(self.settings['ensure_all_syllables_forced'])
        self.ensure_all_syllables_standard_var.set(self.settings['ensure_all_syllables_standard'])
        self.merge_short_entries_var.set(self.settings['merge_short_entries'])
        self.unique_entry_strategy_var.set(
            self._unique_strategy_to_display(self.settings.get('unique_entry_strategy', 'replace'))
        )
        self.redundancy_mode_var.set(
            self._redundancy_mode_to_display(self.settings.get('redundancy_mode', 'active_removal'))
        )
        self.first_onset_as_normal_var.set(self.settings.get('first_onset_as_normal', False))

        sort_mode = self.settings.get('global_sort_reclist', 'grouped')
        if sort_mode not in ('grouped', 'global'):
            sort_mode = 'grouped'
        display_sort = get_text("global_sort_grouped") if sort_mode == 'grouped' else get_text("global_sort_global")
        self.global_sort_reclist_var.set(display_sort)
        self.global_sort_reclist_combo['values'] = [
            get_text("global_sort_grouped"),
            get_text("global_sort_global")
        ]

        if self.settings['separator_format'] == 'R-dash':
            self.separator_format_var.set(get_text("separator_R_dash"))
        else:
            self.separator_format_var.set(get_text("separator_dash_dash"))

        self.oto_sort_var.set(get_text("oto_sort_order") if self.settings['oto_sort'] == 'order' else get_text("oto_sort_category"))
        self.prioritize_semi_vowels_var.set(self.settings['prioritize_semi_vowels'])
        self.prioritize_vowel_transitions_var.set(self.settings['prioritize_vowel_transitions'])
        self.ensure_coda_r_var.set(self.settings['ensure_coda_r'])
        self.ensure_vowel_link_var.set(self.settings['ensure_vowel_link'])
        self.generate_coda_consonant_var.set(self.settings['generate_coda_consonant'])
        self.generate_coda_onset_var.set(self.settings['generate_coda_onset'])
        self.generate_onset_consonant_var.set(self.settings['generate_onset_consonant'])
        self.generate_onset_var.set(self.settings['generate_onset'])
        self.update_generate_onset_state()
        self.update_forced_check_visibility()
        self.update_cv_mode_ui()
        self.previous_mode = mode_var.get()
        
        # 总开关状态默认 False（暂不读取配置）
        self.enable_generate_extra_var.set(False)
        first_sound = self.settings.get('first_sound', 'onset')
        if first_sound == 'none':
            self.first_sound_combobox.set(get_text("first_sound_none"))
        elif first_sound == 'consonant':
            self.first_sound_combobox.set(get_text("first_sound_consonant"))
        else:
            self.first_sound_combobox.set(get_text("first_sound_onset"))
        self.first_sound_internal = first_sound

        # 更新“开头整音视为普通整音”复选框状态（仅开头辅音时可用）
        self.unique_entry_strategy_combo['values'] = [get_text("unique_entry_strategy_replace"), get_text("unique_entry_strategy_backup_alias")]
        self.redundancy_mode_combo['values'] = [get_text("redundancy_mode_active_removal"), get_text("redundancy_mode_keep_all_syllables")]
        self.transition_generation_var.set(self.settings.get('transition_generation', 'all') == 'all')
        self.update_first_onset_check_state()
        self.update_protection_dependent_widgets()

    def _prepare_phoneme_sets(self):
        """预计算规则中的各类音素集合，供 oto 排序使用"""
        self.all_onsets = set()
        self.all_codas = set()
        self.all_consonants = set()
        self.all_vowel_onsets = set()
        self.all_transitions = set()
        for info in self.rules.values():
            self.all_onsets.add(info['onset'])
            if info['coda']:
                self.all_codas.add(info['coda'])
            if info['consonant']:
                self.all_consonants.add(info['consonant'])
            if not info['consonant']:
                self.all_vowel_onsets.add(info['onset'])
            self.all_transitions.update(info['transition'])

    def generate(self):
        if not self.validate_inputs():
            return
        self.update_settings_from_ui()
        warning_messages = []
        if self.settings['first_sound'] == 'none':
            if not self.warning_shown_first_sound:
                if not messagebox.askyesno(get_text("warning"), get_text("first_sound_warning")):
                    return
                self.warning_shown_first_sound = True
            warning_messages.append(get_text("first_sound_warning"))
        if not self.settings['ensure_coda_r']:
            if not self.warning_shown_coda_r:
                if not messagebox.askyesno(get_text("warning"), get_text("coda_r_warning")):
                    return
                self.warning_shown_coda_r = True
            warning_messages.append(get_text("coda_r_warning"))

        if warning_messages:
            self.status_warning_label.config(text="；".join(warning_messages))
        else:
            self.status_warning_label.config(text="")

        rules_path = rules_file_path.get()
        if not rules_path:
            messagebox.showerror(get_text("error"), get_text("no_rules_file"))
            return

        try:
            self.rules = RuleParser.parse(rules_path)
        except Exception as e:
            messagebox.showerror(get_text("error"), get_text("parse_rules_failed").format(e))
            return

        self._prepare_phoneme_sets()   # 预计算音素集合
        # 预计算音节优先级
        self.syllable_priority_cache = {}
        for syl in self.rules:
            info = self.rules[syl]
            cons = info['consonant']
            semi_vowels = [x.strip() for x in self.settings['semi_vowels'].split(',') if x.strip()]
            if self.settings['prioritize_semi_vowels'] and cons in semi_vowels:
                priority = 0
            elif self.settings['prioritize_vowel_transitions'] and not cons and info['transition']:
                priority = 1
            else:
                priority = 2
            self.syllable_priority_cache[syl] = priority

        def get_syllable_priority(syl):
            return self.syllable_priority_cache.get(syl, 2)

        self.debug_log = []

        def priority_sort_key(entry):
            parts = entry.split('_')
            valid = [get_syllable_priority(p) for p in parts if p not in ('-', 'R')]
            if not valid:
                return (2, natural_sort_key(entry))
            min_priority = min(valid)
            return (min_priority, natural_sort_key(entry))
        
        gen = RecordingListGenerator(self.rules, self.settings, self.debug_log)
        self.recording_list, self.forced_set, self.first_sound_entries = gen.generate()

        protected_syllables = set()
        if self.settings['prioritize_semi_vowels']:
            protected_syllables.update(s for s in self.rules if self.rules[s]['consonant'] in self.settings['semi_vowels'].split(','))
        if self.settings['prioritize_vowel_transitions']:
            protected_syllables.update(s for s in self.rules if not self.rules[s]['consonant'] and self.rules[s]['transition'])

        # 根据录音表冗余模式决定是否保护唯一发音
        syllable_count = defaultdict(int)
        for entry in self.recording_list:
            for part in entry.split('_'):
                if part not in ('-', 'R') and part in self.rules:
                    syllable_count[part] += 1

        if self.settings.get('redundancy_mode', 'active_removal') == 'keep_all_syllables':
            # 确保全局完整发音完整：保护所有唯一发音
            protected_syllables.update(s for s, cnt in syllable_count.items() if cnt == 1)
        # 否则积极剔除模式不保护唯一发音，允许剔除（但会触发警告）

        do_remove_redundant = True
        protected_entries = set()
        if self.settings['ensure_all_syllables_forced']:
            protected_entries.update(self.forced_set)
        if self.settings['ensure_all_syllables_standard']:
            protected_entries.update(
                e for e in self.recording_list if e not in self.forced_set and e not in self.first_sound_entries
            )
        # 开头音补全条目始终受保护
        protected_entries.update(self.first_sound_entries)

        # 如果保护开启，则传递 unique_entry_strategy 给 oto 生成
        unique_strategy = self.settings.get('unique_entry_strategy', 'replace')
        first_onset_as_normal = self.settings.get('first_onset_as_normal', False)

        standard_entries = [e for e in self.recording_list if e not in self.forced_set and e not in self.first_sound_entries]
        forced_entries = [e for e in self.recording_list if e in self.forced_set]
        first_sound_entries_list = [e for e in self.recording_list if e in self.first_sound_entries]
        self.recording_list = standard_entries + forced_entries + first_sound_entries_list

        # 准备 OTO 生成用的列表副本，并按需排序（不影响原始列表顺序）
        oto_recording_list = self.recording_list.copy()

        if self.settings['prioritize_semi_vowels'] or self.settings['prioritize_vowel_transitions']:
            oto_recording_list.sort(key=priority_sort_key)

        oto_gen = OTOGenerator(self.rules, self.settings, self.debug_log)
        self.oto_entries, removed = oto_gen.generate(
            oto_recording_list,
            protected_entries=protected_entries,
            protected_syllables=protected_syllables,
            remove_redundant=do_remove_redundant,
            unique_entry_strategy=unique_strategy,
            first_onset_as_normal=first_onset_as_normal,
        )
        # 保护失败条目（已包含在 removed 中）
        unused_protected = getattr(oto_gen, 'unused_protected_entries', [])
        if unused_protected and not getattr(self, 'warning_shown_unused_unique', False):
            self.warning_shown_unused_unique = True
            # 构建警告消息：列出失败条目及其包含的唯一发音
            warning_lines = [get_text("warning_unused_unique")]
            for entry in unused_protected:
                # 找出该条目中 syllable_count == 1 的音节
                unique_syls = []
                for part in entry.split('_'):
                    if part not in ('-', 'R') and part in self.rules and syllable_count.get(part, 0) == 1:
                        unique_syls.append(part)
                if unique_syls:
                    warning_lines.append(f"{entry} -> {', '.join(unique_syls)}")
                else:
                    warning_lines.append(entry)
            messagebox.showwarning(
                get_text("warning"),
                "\n".join(warning_lines)
            )
        else:
            self.warning_shown_unused_unique = True  # 避免重复警告
        # 注意：oto_gen.generate 返回的 removed 是基于排序后的列表，
        # 但条目字符串与原始列表一致，可以直接用于移除。
        # 在 oto_gen.generate 调用之后
        for rep in oto_gen.report:
            status = rep['status']
            entry = rep['entry']
            alias_str = ', '.join(rep['aliases'])
            if rep['new_aliases']:
                new_alias_str = ', '.join(rep['new_aliases'])
            else:
                new_alias_str = '无'
            self.debug_log.append(f"[oto报告] 条目: {entry} | 状态: {status} | 别名: {alias_str} | 新增: {new_alias_str}")

        total_aliases = sum(len(rep['aliases']) for rep in oto_gen.report)
        self.debug_log.append(f"[oto汇总] 处理条目数: {len(oto_gen.report)}，生成别名总数: {total_aliases}")

        self.recording_list = [line for line in self.recording_list if line not in removed]
        self.debug_log.append(f"[冗余剔除] 剔除条目数: {len(removed)}")

        display_removed = removed
        self.removed_text.config(state=tk.NORMAL)
        self.removed_text.delete("1.0", tk.END)
        for item in display_removed:
            display_item = convert_separator_display(item, self.settings['separator_format'])
            self.removed_text.insert(tk.END, display_item + "\n")
        self.removed_text.config(state=tk.DISABLED)
        self.removed_count_label.config(text=get_text("removed_count").format(len(display_removed)))

        used_syllables = set()
        for entry in self.recording_list:
            for s in entry.split('_'):
                if s != '-' and s != 'R':
                    used_syllables.add(s)
        unused_syllables = set(self.rules.keys()) - used_syllables

        # 将保护失败条目中的唯一发音加入未使用列表（这些条目已被移除）
        for entry in unused_protected:
            for s in entry.split('_'):
                if s not in ('-', 'R') and s in self.rules and syllable_count.get(s, 0) == 1:
                    unused_syllables.add(s)
                    
        self.unused_text.config(state=tk.NORMAL)
        self.unused_text.delete("1.0", tk.END)
        for syl in sorted(unused_syllables, key=natural_sort_key):
            display_syl = convert_separator_display(syl, self.settings['separator_format'])
            self.unused_text.insert(tk.END, display_syl + "\n")
        self.unused_text.config(state=tk.DISABLED)

        forced_final = [e for e in self.recording_list if e in self.forced_set]
        first_sound_final = [e for e in self.recording_list if e in self.first_sound_entries]
        standard_final = [e for e in self.recording_list if e not in self.forced_set and e not in self.first_sound_entries]

        if self.settings.get('global_sort_reclist', 'grouped') == 'global':
            # 全局自然排序
            self.recording_list.sort(key=natural_sort_key)
        else:
            # 分组排序：强制 → 标准 → 补全（如有） → 开头音
            if self.settings.get('ensure_all_syllables_standard', True):
                sort_key = natural_sort_key
            else:
                sort_key = priority_sort_key

            forced_final.sort(key=sort_key)
            standard_final.sort(key=sort_key)
            first_sound_final.sort(key=sort_key)
            self.recording_list = forced_final + standard_final + first_sound_final

        self.update_result_display()
        self.update_debug_display()

    def update_result_display(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        for entry in self.recording_list:
            display_entry = convert_separator_display(entry, self.settings['separator_format'])
            self.result_text.insert(tk.END, display_entry + "\n")
        self.result_text.config(state=tk.DISABLED)

        self.oto_text.config(state=tk.NORMAL)
        self.oto_text.delete("1.0", tk.END)
        if self.settings['oto_sort'] == 'category':
            sorted_oto = self.sort_oto_entries(self.oto_entries)
        else:
            sorted_oto = self.oto_entries
        oto_output = "\n".join(
            f"{e['filename']}={e['alias']},{e['offset']},{e['consonant']},{e['cutoff']},{e['preutterance']},{e['overlap']}"
            for e in sorted_oto
        )
        self.oto_text.insert(tk.END, oto_output)
        self.oto_text.config(state=tk.DISABLED)

        self.reclist_line_count_label.config(text=get_text("line_count_reclist").format(len(self.recording_list)))
        self.oto_line_count_label.config(text=get_text("line_count_oto").format(len(self.oto_entries)))
        self.export_reclist_button.config(state="normal")
        self.export_oto_button.config(state="normal")

    def update_debug_display(self):
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete("1.0", tk.END)
        self.debug_text.insert(tk.END, "=== 参数快照 ===\n")
        for key, value in self.settings.items():
            self.debug_text.insert(tk.END, f"{key}: {value}\n")
        self.debug_text.insert(tk.END, "\n=== 生成日志 ===\n")
        for log_line in self.debug_log:
            self.debug_text.insert(tk.END, log_line + "\n")
        self.debug_text.config(state=tk.DISABLED)

    def sort_oto_entries(self, entries):
        # 使用预计算的音素集合，避免每次排序都重新构建
        all_onsets = self.all_onsets
        all_codas = self.all_codas
        all_consonants = self.all_consonants
        all_vowel_onsets = self.all_vowel_onsets
        all_transitions = self.all_transitions

        def get_category(alias):
            # 返回 (主类别, 子优先级)
            if alias.startswith('- '):
                return (0, 0)  # 开头音
            if alias in all_onsets:
                return (1, 0)  # 单独整音
            if alias in all_transitions:
                return (2, 0)  # 过渡音
            if alias.endswith(' R') or alias.endswith(' -'):
                return (3, 1)  # 尾音结尾（coda_R），子优先级 1 排最后
            if ' ' in alias:
                first, second = alias.split(' ', 1)
                if first in all_codas:
                    if second in all_consonants:
                        return (3, 0)  # 尾音到辅音
                    elif second in all_vowel_onsets:
                        return (4, 0)  # 尾音到元音
                elif first in all_onsets and second in all_consonants:
                    return (5, 0)  # 整音到辅音
            return (6, 0)  # 其他

        def sort_key(entry):
            cat, sub = get_category(entry['alias'])
            offset = entry['offset']
            return (cat, sub, offset)  # 始终是三元组，类型一致

        # Python 的 sorted 是稳定的，相同键时保持原始顺序
        return sorted(entries, key=sort_key)
        
    def export_reclist(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for entry in self.recording_list:
                        f.write(convert_separator_display(entry, self.settings['separator_format']) + "\n")
                messagebox.showinfo(get_text("success"), get_text("recording_list_saved").format(filename))
            except Exception as e:
                messagebox.showerror(get_text("error"), get_text("failed_to_export_recording_list").format(e))

    def export_oto(self):
        filename = filedialog.asksaveasfilename(defaultextension=".ini",
                                                filetypes=(("INI files", "*.ini"), ("All files", "*.*")))
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    if self.settings['oto_sort'] == 'category':
                        entries_to_write = self.sort_oto_entries(self.oto_entries)
                    else:
                        entries_to_write = self.oto_entries
                    for e in entries_to_write:
                        f.write(f"{e['filename']}={e['alias']},{e['offset']},{e['consonant']},{e['cutoff']},{e['preutterance']},{e['overlap']}\n")
                messagebox.showinfo(get_text("success"), get_text("oto_configuration_saved").format(filename))
            except Exception as e:
                messagebox.showerror(get_text("error"), get_text("failed_to_export_oto_configuration").format(e))

    def switch_language(self, event=None):
        global current_language
        current_language = language_var.get()
        load_language_file()
        self.update_ui_text()
        self.update_first_onset_check_state()

    def update_ui_text(self):
        self.master.title(get_text("title"))
        self.rules_file_label.config(text=get_text("rules_file_label"))
        self.browse_button.config(text=get_text("browse_button"))
        self.generate_button.config(text=get_text("generate_button"))
        self.export_reclist_button.config(text=get_text("export_reclist_button"))
        self.export_oto_button.config(text=get_text("export_oto_button"))
        self.mode_label.config(text=get_text("mode_label"))
        self.max_syllables_label.config(text=get_text("max_syllables_label"))
        self.generation_mode_label.config(text=get_text("generation_mode_label"))
        self.bpm_label.config(text=get_text("bpm_label"))
        self.leading_silence_label.config(text=get_text("leading_silence_label"))
        self.max_alternatives_label.config(text=get_text("max_alternatives_label"))
        self.ensure_all_syllables_forced_check.config(text=get_text("ensure_all_syllables_forced_label"))
        self.ensure_all_syllables_standard_check.config(text=get_text("ensure_all_syllables_standard_label"))
        self.merge_short_entries_check.config(text=get_text("merge_short_entries_label"))
        self.prioritize_semi_vowels_check.config(text=get_text("prioritize_semi_vowels_label"))
        self.prioritize_vowel_transitions_check.config(text=get_text("prioritize_vowel_transitions_label"))
        self.ensure_coda_r_check.config(text=get_text("ensure_coda_r_label"))
        self.ensure_vowel_link_check.config(text=get_text("ensure_vowel_link_label"))
        self.generate_coda_consonant_check.config(text=get_text("generate_coda_consonant_label"))
        self.generate_coda_onset_check.config(text=get_text("generate_coda_onset_label"))
        self.generate_onset_consonant_check.config(text=get_text("generate_onset_consonant_label"))
        self.generate_onset_check.config(text=get_text("generate_onset_label"))
        self.semi_vowels_label.config(text=get_text("semi_vowels_label"))
        self.first_sound_label.config(text=get_text("first_sound_label"))
        self.transition_generation_label.config(text=get_text("transition_generation_label"))
        self.transition_generation_check.config(text=get_text("transition_generation_all"))
        self.separator_label.config(text=get_text("separator_label"))
        self.oto_sort_label.config(text=get_text("oto_sort_label"))
        self.language_label.config(text=get_text("language_label"))
        self.load_config_button.config(text=get_text("load_config_button"))
        self.save_config_button.config(text=get_text("save_config_button"))
        self.notebook.tab(0, text=get_text("recording_list"))
        self.notebook.tab(1, text=get_text("oto_configuration"))
        self.notebook.tab(2, text=get_text("removed_title"))
        self.notebook.tab(3, text=get_text("unused_syllables_title"))
        self.notebook.tab(4, text=get_text("debug_title"))
        self.protect_frame.config(text=get_text("protect_frame"))
        self.priority_frame.config(text=get_text("priority_frame"))
        self.other_frame.config(text=get_text("other_frame"))
        self.generate_frame.config(text=get_text("generate_frame_label"))
        self.enable_generate_extra_check.config(text=get_text("enable_generate_extra"))
        self.language_combobox['values'] = available_languages
        self.reclist_line_count_label.config(text=get_text("line_count_reclist").format(len(self.recording_list)))
        self.oto_line_count_label.config(text=get_text("line_count_oto").format(len(self.oto_entries)))
        self.unique_entry_strategy_label.config(text=get_text("unique_entry_strategy_label"))
        self.unique_entry_strategy_combo['values'] = [
            get_text("unique_entry_strategy_replace"),
            get_text("unique_entry_strategy_backup_alias")
        ]
        self.first_onset_as_normal_check.config(text=get_text("first_onset_as_normal_label"))
        self.redundancy_mode_label.config(text=get_text("redundancy_mode_label"))
        self.redundancy_mode_combo['values'] = [
            get_text("redundancy_mode_active_removal"),
            get_text("redundancy_mode_keep_all_syllables")
        ]
        self.global_sort_reclist_label.config(text=get_text("global_sort_reclist_label"))
        self.global_sort_reclist_combo['values'] = [
            get_text("global_sort_grouped"),
            get_text("global_sort_global")
        ]
        self.update_onset_label()
         
# ===== 程序入口 =====
if __name__ == "__main__":
    available_languages = load_language_file()
    if not os.path.exists(config_file):
        default_settings = {
            'max_syllables_per_sentence': 8,
            'mode': 'vccv-cvvc',
            'separator_format': 'R-dash',
            'oto_sort': 'order',
            'merge_short_entries': False,
            'bpm': 120,
            'leading_silence': 100,
            'max_alternatives': 0,
            'use_consonant_for_first_syllable': False,
            'semi_vowels': 'v,w,y',
            'prioritize_semi_vowels': False,
            'prioritize_vowel_transitions': False,
            'transition_generation': 'all',
            'first_sound': 'onset',
            'ensure_coda_r': True,
            'ensure_vowel_link': True,
            'generate_coda_consonant': False,
            'generate_coda_onset': False,
            'generate_onset_consonant': False,
            'generate_onset': False,
            'generation_mode': 'none',
            'ensure_all_syllables_forced': True,
            'ensure_all_syllables_standard': True
        }
        save_config_file(config_file, default_settings)

    app = Application(root)
    root.deiconify()
    root.mainloop()