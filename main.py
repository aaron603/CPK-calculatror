# -*- coding: utf-8 -*-

import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Menu
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


class CPKCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("深科技Mes导出RRU生产测试数据CPK分析器")

        self.create_widgets()
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=3, pady=10, sticky='ew')

        self.create_menu()

    def create_widgets(self):
        self.file_label = tk.Label(self.root, text="选择待分析CSV源文件:")
        self.file_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.grid(row=0, column=1, padx=10, pady=5)

        self.browse_button = tk.Button(self.root, text="浏览", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=5)

        self.split_button = tk.Button(self.root, text="拆分CSV文件", command=self.split_csv, width=20)
        self.split_button.grid(row=1, column=1, pady=10)

        self.config_button = tk.Button(self.root, text="生成配置文件", command=self.generate_config, width=20)
        self.config_button.grid(row=2, column=1, pady=10)

        self.extract_button = tk.Button(self.root, text="提取测试项数据", command=self.extract_test_data, width=20)
        self.extract_button.grid(row=3, column=1, pady=10)

        self.cpk_button = tk.Button(self.root, text="计算CPK", command=self.calculate_cpk, width=20)
        self.cpk_button.grid(row=4, column=1, pady=10)

    def create_menu(self):
        menu_bar = Menu(self.root)
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="帮助", command=self.show_help)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menu_bar)

    def show_help(self):
        help_text = (
            "该程序为按照深科技Mes系统导出的RRU测试数据的csv文件，按照测试项目分别生成cpk，以供研发分析之用，可以按照导出csv数据文件，逐一分析cpk。\n"
            "1）“选择csv文件”浏览框，点击右侧“浏览”，选在深科技mes系统导出需要分析测试工位的数据源文件；\n"
            "2）“拆分csv文件”按钮作用：选择测试数据所在csv文件后，点击此按钮开始按照模块为单位拆分测试数据，并自动保存为一个单独目录split_files。测试fail的模块文件命名末尾会自动增加fail，用户如果不想这些失败模块数据参与cpk运算，可以在文件拆分后cpk计算前，手动删除这些失败的模块数据，以避免其参与运算；\n"
            "3）“生成配置文件”按钮作用，点击此按钮后，会自动在用户选择目录下生成一个配置文件，用户可以根据需要，把需要参与计算cpk的测试项目，对应测试项目配置为True并保存，默认值全部为False；\n"
            "4）“提取测试项数据”按钮作用，点击此按钮后，用户选择根据程序提示选择拆分后RRU模块测试数据所在目录，程序会自动将该目录下的模块数据按照测试项目为单位进行提取，生成便于cpk计算的测试项目为单位的文件，保存在test_data文件夹下；\n"
            "5）“计算CPK”按钮作用，点击此按钮后，用户需要先根据提示选择计算cpk的配置文件（注意需要计算cpk的测试项目，用户需要先在配置文件修改为True）；选择完成配置文件后，程序会提示继续选择计算cpk文件所在的提取数据目录，然后程序会自动开始计算cpk（程序会自动跳过测试项目为fail的值，fail结果不参与cpk计算），并画cpk正态分布图保存在cpk_plots目录，并会生成日志，自动保存在cpk_results结果目录中。"
        )
        messagebox.showinfo("帮助", help_text)

    def browse_file(self):
        self.file_entry.delete(0, tk.END)
        file_path = filedialog.askopenfilename(filetypes=[("CSV文件", "*.csv")])
        if file_path:
            self.file_entry.insert(0, file_path)

    def split_csv(self):
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("错误", "请选择一个CSV文件。")
            return

        output_dir = filedialog.askdirectory(title="请选择保存拆分文件路径")
        if not output_dir:
            messagebox.showerror("错误", "请选择一个输出目录。")
            return

        split_dir = os.path.join(output_dir, "split_files")
        os.makedirs(split_dir, exist_ok=True)

        df = pd.read_csv(file_path)
        total_groups = len(df.groupby(['SeqNO', 'PrdSN']))
        progress_step = 100 / total_groups

        for (seq_no, prd_sn), group in df.groupby(['SeqNO', 'PrdSN']):
            if len(group['result'].unique()) > 1:
                messagebox.showerror("错误", f"{prd_sn}_{seq_no} 模块的 result 列值不一致。")
                continue

            result = group['result'].iloc[0]
            if result.lower() == 'fail':
                file_name = f"{prd_sn}_{seq_no}_fail.csv"
            else:
                file_name = f"{prd_sn}_{seq_no}.csv"
            output_path = os.path.join(split_dir, file_name)
            group.to_csv(output_path, index=False)

            self.progress.set(self.progress.get() + progress_step)
            self.root.update_idletasks()

        messagebox.showinfo("成功", "CSV文件拆分成功。")
        self.progress.set(0)

    def generate_config(self):
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("错误", "请选择一个CSV文件。")
            return

        output_dir = filedialog.askdirectory(title="请选择生成配置文件保存路径")
        if not output_dir:
            messagebox.showerror("错误", "请选择一个输出目录。")
            return

        df = pd.read_csv(file_path)
        test_points = df['TestPointNumber'].unique()
        config_df = pd.DataFrame({
            'TestPointNumber': test_points,
            'CalculateCPK': [False] * len(test_points)
        })

        config_path = os.path.join(output_dir, "config.csv")
        config_df.to_csv(config_path, index=False)
        messagebox.showinfo("成功", "配置文件生成成功。")

    def extract_test_data(self):
        split_dir = filedialog.askdirectory(title="请选择拆分文件目录")
        if not split_dir:
            messagebox.showerror("错误", "请选择拆分文件的目录。")
            return

        test_data_dir = os.path.join(os.path.dirname(split_dir), "test_data")
        os.makedirs(test_data_dir, exist_ok=True)

        total_files = len([name for name in os.listdir(split_dir) if os.path.isfile(os.path.join(split_dir, name))])
        progress_step = 100 / total_files

        for root_dir, _, files in os.walk(split_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                df = pd.read_csv(file_path)
                for test_point, group in df.groupby('TestPointNumber'):
                    output_path = os.path.join(test_data_dir, f"{test_point}.csv")
                    group[['SeqNO', 'PrdSN', 'LimitLow', 'LimitHigh', 'TestData', 'Result2']].to_csv(output_path,
                                                                                                     index=False,
                                                                                                     mode='a',
                                                                                                     header=not os.path.exists(
                                                                                                         output_path))

                self.progress.set(self.progress.get() + progress_step)
                self.root.update_idletasks()

        messagebox.showinfo("成功", "测试数据提取成功。")
        self.progress.set(0)

    def calculate_cpk(self):
        config_path = filedialog.askopenfilename(filetypes=[("CSV文件", "*.csv")], title="请选择配置文件")
        if not config_path:
            messagebox.showerror("错误", "请选择配置文件。")
            return

        test_data_dir = filedialog.askdirectory(title="请选择计算CPK测试项目数据所在文件夹")
        if not test_data_dir:
            messagebox.showerror("错误", "请选择一个测试数据目录。")
            return

        output_dir = os.path.dirname(test_data_dir)
        cpk_results_dir = os.path.join(output_dir, "cpk_results")
        cpk_plots_dir = os.path.join(output_dir, "cpk_plots")
        os.makedirs(cpk_results_dir, exist_ok=True)
        os.makedirs(cpk_plots_dir, exist_ok=True)

        config = pd.read_csv(config_path)
        total_files = len(config[config['CalculateCPK']])
        progress_step = 100 / total_files

        low_cpk_list = []

        for _, row in config.iterrows():
            if row['CalculateCPK']:
                test_point = row['TestPointNumber']
                file_path = os.path.join(test_data_dir, f"{test_point}.csv")
                if not os.path.exists(file_path):
                    continue

                df = pd.read_csv(file_path)
                df = df[df['Result2'].str.lower() == 'pass']
                if df.empty:
                    messagebox.showwarning("警告", f"{test_point} 没有可用的数据进行CPK计算。")
                    continue

                cpk, plot_path = self.plot_cpk(df, test_point, cpk_plots_dir)

                if cpk < 1.33:
                    low_cpk_list.append([test_point, cpk])

                with open(os.path.join(cpk_results_dir, f"{test_point}_cpk.log"), 'w') as log_file:
                    for _, row in df.iterrows():
                        log_file.write(f"{row.to_dict()}\n")

                self.progress.set(self.progress.get() + progress_step)
                self.root.update_idletasks()

        if low_cpk_list:
            low_cpk_df = pd.DataFrame(low_cpk_list, columns=['TestPoint', 'CPK'])
            low_cpk_df.to_csv(os.path.join(cpk_results_dir, "low_cpk.csv"), index=False)

        messagebox.showinfo("成功", "CPK计算完成。")
        self.progress.set(0)

    def plot_cpk(self, df, test_point, output_dir):
        data = df['TestData']
        mean = data.mean()
        std = data.std()
        lsl = df['LimitLow'].iloc[0]
        usl = df['LimitHigh'].iloc[0]

        cpk = min((usl - mean) / (3 * std), (mean - lsl) / (3 * std))

        plt.figure()
        plt.hist(data, bins=30, density=True, alpha=0.6, color='g')

        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mean, std)
        plt.plot(x, p, 'k', linewidth=2)

        plt.axvline(lsl, color='r', linestyle='dashed', linewidth=1)
        plt.axvline(usl, color='r', linestyle='dashed', linewidth=1)
        plt.axvline(mean, color='b', linestyle='dashed', linewidth=1)

        plt.text(lsl, plt.ylim()[1] * 0.9, f'LSL: {lsl}', color='r', horizontalalignment='right')
        plt.text(usl, plt.ylim()[1] * 0.9, f'USL: {usl}', color='r', horizontalalignment='left')
        plt.text(mean, plt.ylim()[1] * 0.9, f'Mean: {mean:.2f}', color='b', horizontalalignment='center')

        title = f"{test_point} - CPK: {cpk:.2f}"
        plt.title(title)

        plot_path = os.path.join(output_dir, f"{test_point}_cpk.png")
        plt.savefig(plot_path)
        plt.close()

        return cpk, plot_path


if __name__ == "__main__":
    root = tk.Tk()
    app = CPKCalculatorApp(root)
    root.mainloop()
