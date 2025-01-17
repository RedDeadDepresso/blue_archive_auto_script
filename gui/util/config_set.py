import json
import os
import re

from gui.util.customed_ui import BoundComponent
from gui.util.translator import baasTranslator as bt


class ConfigSet:
    def __init__(self, config_dir):
        super().__init__()
        self.config = None
        self.gui_config = None
        self.server_mode = 'CN'
        self.inject_comp_list = []
        self.inject_config_list = []
        self.window = None
        self.main_thread = None
        self.static_config = None
        self.config_dir = None
        self.static_config_path = None
        if os.path.exists(f'config/{config_dir}/config.json'):  # relative path
            self.config_dir = os.path.abspath(f'config/{config_dir}')
            self.static_config_path = os.path.dirname(self.config_dir) + '/static.json'
        elif os.path.exists(f'{config_dir}/config.json'):  # absolute path
            self.config_dir = config_dir
            self.static_config_path = os.path.abspath(os.path.dirname(config_dir) + '/static.json')
        else:
            raise FileNotFoundError(f'config/{config_dir}/config.json not found')
        self.signals = {}
        self._init_config()

    def _init_config(self):
        with open(os.path.join(self.config_dir, "config.json"), 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        with open(self.static_config_path, 'r', encoding='utf-8') as f:
            self.static_config = json.load(f)
        if self.config['server'] == '国服' or self.config['server'] == 'B服':
            self.server_mode = 'CN'
        elif self.config['server'] in ['国际服', '国际服青少年', '韩国ONE']:
            self.server_mode = 'Global'
        elif self.config['server'] == '日服':
            self.server_mode = 'JP'

    def get(self, key):
        self._init_config()
        value = self.config.get(key)
        return bt.tr('ConfigTranslation', value)

    def get_origin(self, key):
        self._init_config()
        return self.config.get(key)

    def set(self, key, value):
        self._init_config()
        value = bt.undo(value)
        self.config[key] = value
        self.save()
        self.dynamic_update(key)

    def save(self):
        with open(os.path.join(self.config_dir, "config.json"), 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def dynamic_update(self, key):
        if key not in self.inject_config_list: return
        for comp in self.inject_comp_list:
            comp.config_updated(key)

    def update(self, key, value):
        self.set(key, value)

    def __getitem__(self, item: str):
        return self.config[item]

    def check(self, key, value):
        with open(os.path.join(self.config_dir, "config.json"), 'r', encoding='utf-8') as f:
            new_config = json.load(f)
        return new_config.get(key) == value

    def add_signal(self, key, signal):
        self.signals[key] = signal

    def get_signal(self, key):
        return self.signals.get(key)

    def set_window(self, window):
        self.window = window

    def get_window(self):
        return self.window

    def set_main_thread(self, thread):
        self.main_thread = thread

    def get_main_thread(self):
        return self.main_thread

    def inject(self, component, string_rule, attribute="setText"):
        """
        Inject a component with a string rule
        :param component: Component to inject
        :param string_rule: String rule
        :param attribute: Attribute to inject (default is setText)
        :return: BoundComponent, which can be ignored
        """
        bounded = BoundComponent(component, string_rule, self, attribute)
        self.inject_config_list.extend(re.findall(r'{(.*?)}', string_rule))
        self.inject_comp_list.append(bounded)
        return bounded

    def update_create_quantity_entry(self):
        dft = self.static_config["create_item_order"][self.server_mode]["basic"]
        dft_list = [item for sublist in dft.values() for item in sublist]
        pop_list = []
        for key in self.config["create_item_holding_quantity"]:
            if key not in dft_list:
                pop_list.append(key)
        for key in pop_list:
            self.config["create_item_holding_quantity"].pop(key)

        for entry in dft_list:
            if entry not in self.config["create_item_holding_quantity"]:
                self.config["create_item_holding_quantity"][entry] = -1
        self.save()
