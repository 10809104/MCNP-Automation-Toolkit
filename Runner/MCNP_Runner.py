# ================= KikKoh @2026 =================
# ================ 最終版：待機模擬復古終端 ============
import os
import ctypes
import time
import threading

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import psutil

import random
import msvcrt

from pathlib import Path
import shutil
import sys
import uuid
import subprocess

'''整體架構
Main Thread
 ├── Manager Thread
 │     ├── Worker Threads
 │     └── display_status (可暫停)
 │
 ├── ResourceMonitor Thread
 │
 └── RetroRunner Thread
'''

class ConfigLoader:
    def __init__(self):
        # 初始化主視窗並隱藏
        self.root = tk.Tk()
        self.root.withdraw()
        # 確保對話框彈在最前面
        self.root.attributes("-topmost", True)

    def select_file(self, title="選擇檔案", initial_dir=None, default_file=None):
        """選擇單一檔案，若預設檔案存在則直接回傳"""
        if initial_dir is None:
            initial_dir = os.getcwd()

        if default_file and os.path.exists(default_file):
            return os.path.abspath(default_file)

        path = filedialog.askopenfilename(
            title=title,
            initialdir=initial_dir,
            filetypes=[("batch批次檔", ".bat")]
        )
        return path if path else None

    def select_folder(self, title="選擇資料夾", initial_dir=None):
        """選擇資料夾"""
        if initial_dir is None:
            initial_dir = os.getcwd()

        path = filedialog.askdirectory(
            title=title,
            initialdir=initial_dir
        )
        return path if path else None

    def select_input_files(self, title="選擇 .i 檔案", initial_dir=None):
        """開啟一個自定義對話框來管理多個 MCNP 輸入檔"""
        files = []
        
        # 建立一個 Toplevel 視窗作為自定義對話框
        dialog = tk.Toplevel(self.root)
        dialog.title("待處理檔案清單")
        dialog.attributes("-topmost", True)

        # 介面組件
        listbox = tk.Listbox(dialog, width=70, height=15, selectmode=tk.MULTIPLE)
        listbox.pack(padx=10, pady=10)

        def add_files():
            new_paths = filedialog.askopenfilenames(parent=dialog, title=title, initialdir=initial_dir, filetypes=[("i檔", "*.i"), ("其他檔案", "*.*")])
            for p in new_paths:
                if p not in files:
                    files.append(p)
                    listbox.insert(tk.END, p)

        def remove_selected():
            selected = listbox.curselection()
            for i in reversed(selected):
                files.pop(i)
                listbox.delete(i)

        def clear_all():
            files.clear()
            listbox.delete(0, tk.END)

        # 按鈕列
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text=" ＋ 新增檔案 ", command=add_files).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=" － 刪除選取 ", command=remove_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=" ✘ 清空全部 ", command=clear_all).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=" ✔ 確認完成 ", command=dialog.destroy, bg="#e1e1e1").pack(side=tk.LEFT, padx=20)

        # 鎖定焦點直到視窗關閉
        dialog.grab_set()
        self.root.wait_window(dialog)
        
        return files
        
    def select_two_numbers(self, title="選擇兩個數值", min_val=10, max_val=85):
        """開啟對話框讓使用者選擇兩個獨立數字"""

        result = {"num1": None, "num2": None}

        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)

        tk.Label(dialog, text="CPU 使用上限(%):").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(dialog, text="RAM 使用上限(%):").grid(row=1, column=0, padx=10, pady=10)

        var1 = tk.IntVar(value=70)
        var2 = tk.IntVar(value=70)

        def validate(value):
            if value == "":
                return True
            if value.isdigit():
                v = int(value)
                return min_val <= v <= max_val
            return False

        vcmd = (dialog.register(validate), "%P")

        spin1 = ttk.Spinbox(
            dialog,
            from_=min_val,
            to=max_val,
            textvariable=var1,
            validate="key",
            validatecommand=vcmd,
            width=6
        )
        spin2 = ttk.Spinbox(
            dialog,
            from_=min_val,
            to=max_val,
            textvariable=var2,
            validate="key",
            validatecommand=vcmd,
            width=6
        )

        spin1.grid(row=0, column=1, padx=10, pady=10)
        spin2.grid(row=1, column=1, padx=10, pady=10)

        def confirm():
            result["num1"] = var1.get()
            result["num2"] = var2.get()
            dialog.destroy()

        tk.Button(dialog, text="✔ 確認", command=confirm, bg="#e1e1e1").grid(
            row=2, column=0, columnspan=2, pady=15
        )

        dialog.grab_set()
        self.root.wait_window(dialog)

        return result["num1"], result["num2"]

    def close(self):
        """釋放 Tkinter 資源"""
        self.root.destroy()
        
import tkinter as tk

def custom_warning(title, message, button_text="確定"):
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗

    win = tk.Toplevel(root)
    win.title(title)
    win.resizable(False, False)

    # 驚嘆號 + 訊息
    tk.Label(win, text=f"⚠️ {message}", padx=20, pady=20, font=("Arial", 12)).pack()
    tk.Button(win, text=button_text, command=win.destroy, width=15, font=("Arial", 12)).pack(pady=(0,20))
    
    # 浮在最上層
    win.attributes('-topmost', True)
    win.lift()
    win.focus_force()

    # 模態視窗
    win.grab_set()
    root.mainloop()
class ResourceMonitor:
    def __init__(self, cpu_limit=None, ram_limit=70, cooldown=5):
        self.logical_cores = psutil.cpu_count(logical=True)
        
        if self.logical_cores > 1 and cpu_limit == None:
            self.cpu_limit = ((self.logical_cores - 1) / self.logical_cores) * 100
        elif self.logical_cores == 1 and cpu_limit != None:
            self.cpu_limit = 80
        else:
            self.cpu_limit = cpu_limit
        self.ram_limit = ram_limit
        self.cooldown = cooldown
        
        self.known_pids = self._get_current_pids()
        self.last_alert_time = 0
        
        self._running = False
        
        # for 已啟動之mcnp
        self.tracked_pids = set()
        self.pid_lock = threading.Lock()
        psutil.cpu_percent(interval=None)
        # --- 啟動冷卻控制 ---
        self.start_cooldown = 15      # 秒（可調）
        self.last_start_time = 0     # 上次啟動時間
        self.smoothed_cpu = 0
        self.smoothed_avg_cpu = 0
        self.alpha = 0.3  # 平滑係數
        self.ram_safety_buffer = 0  # %（可調）
        
    # ------------------------
    # PID / 系統進程判斷
    # ------------------------
    def _get_current_pids(self):
        """抓取當前所有 PID"""
        try:
            return set(p.pid for p in psutil.process_iter())
        except Exception as e:
            print(f"[*] 初始化 PID 清單失敗: {e}")
            return set()

    def _is_system_process(self, proc):
        """判斷是否為系統進程"""
        try:
            if not proc.is_running(): 
                return True
            exe = proc.exe().lower()
            win = os.environ.get("WINDIR", "").lower()
            return exe.startswith(win) or "system32" in exe
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return True

    # ------------------------
    # 單次掃描
    # ------------------------
    def scan(self):
        try:
            cpu_now = psutil.cpu_percent(interval=1)
            ram_now = psutil.virtual_memory().percent

            current_processes = list(psutil.process_iter(['pid', 'name']))
            current_pids = {p.info['pid'] for p in current_processes}
            self.known_pids &= current_pids
            triggered = False

            for p in current_processes:
                pid = p.info['pid']
                p_name = p.info['name']
                if pid in self.known_pids:
                    continue
                self.known_pids.add(pid)
                if p_name in ('mcnp6.exe', 'OpenConsole.exe', 'cmd.exe', 'python.exe', 'AdskExecutorProxy.exe'):
                        self.known_pids.add(pid) # 加入白名單，下次不掃
                        continue

                try:
                    proc = psutil.Process(pid)
                    if self._is_system_process(proc):
                        continue

                    if cpu_now > self.cpu_limit or ram_now > self.ram_limit:
                        now = time.time()
                        if now - self.last_alert_time > self.cooldown:
                            print(f"\n[!] 偵測到使用者活動: {p.info['name']} (PID: {pid})")
                            self.last_alert_time = now
                            custom_warning(
                                "系統負載警告",
                                f"叫你玩'{p.info['name']}'的哦!\n\n當前負載: CPU {cpu_now}%, RAM {ram_now}%\n折不動了啦",
                                button_text="ㄚ我就是要當巴咩"
                            )
                            triggered = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            return triggered, cpu_now, ram_now

        except Exception as e:
            print(f"[*] 監控掃描發生錯誤: {e}")
            return False, 0, 0
        
    def _loop(self):
        while self._running:
            self.scan()
            time.sleep(1)
            
    # ------------------------
    # 啟動 / 停止監控
    # ------------------------
    def start(self):
        if not self._running:
            self._running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            
    def stop(self):
        self._running = False
        if self.thread:
            self.thread.join(timeout=2)  # 等 thread 安全結束
            
    # ------------------------
    # 其他功能
    # ------------------------
    def add_pid(self, pid):
        with self.pid_lock:
            psutil.Process(pid).cpu_percent(interval=None)
            self.tracked_pids.add(pid)

    def remove_pid(self, pid):
        with self.pid_lock:
            self.tracked_pids.discard(pid)
    
    def is_system_okay(self):
        """檢查系統資源是否低於設定門檻"""
        # --- 冷卻保護 ---
        if time.time() - self.last_start_time < self.start_cooldown:
            return False

        # --- 系統資源 ---
        current_cpu = psutil.cpu_percent(interval=None)

        self.smoothed_cpu = (
            self.alpha * current_cpu +
            (1 - self.alpha) * self.smoothed_cpu
        )

        vm = psutil.virtual_memory()
        current_ram_percent = vm.percent
        total_ram = vm.total

        with self.pid_lock:
            processes = []

            for pid in list(self.tracked_pids):
                try:
                    p = psutil.Process(pid)
                    processes.append(p)
                    processes.extend(p.children(recursive=True))
                except psutil.NoSuchProcess:
                    self.tracked_pids.discard(pid)

        # warmup（不要加總）
        for proc in processes:
            try:
                proc.cpu_percent(None)
            except psutil.NoSuchProcess:
                pass
        
        time.sleep(0.1)
        
        worker_cpu = 0
        worker_ram = 0

        for proc in processes:
            try:
                worker_cpu += proc.cpu_percent(None)
                worker_ram += proc.memory_info().rss
            except psutil.NoSuchProcess:
                pass

        worker_count = len(self.tracked_pids)

        # --- 預測增量 ---
        if worker_count > 0:
            avg_cpu = (worker_cpu / worker_count) / self.logical_cores
            self.smoothed_avg_cpu = (
                self.alpha * avg_cpu +
                (1 - self.alpha) * self.smoothed_avg_cpu
            )
            avg_cpu = self.smoothed_avg_cpu
            avg_ram = worker_ram / worker_count
        else:
            avg_cpu = (1 / self.logical_cores *100)
            avg_ram = 3 * 1024 * 1024 * 1024

        predicted_cpu = self.smoothed_cpu + avg_cpu
        predicted_ram = current_ram_percent + (avg_ram / total_ram * 100)
        return (
            predicted_cpu <= self.cpu_limit and
            predicted_ram <= (self.ram_limit - self.ram_safety_buffer) and
            worker_count < max(1, self.logical_cores - 2)
        )
        
    def get_status_string(self):
        """方便在 DOS 介面顯示目前的資源狀況"""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return f"CPU: {cpu}% | RAM: {ram}%"
        
class RetroRunner(threading.Thread):
    def __init__(self, manager, duration=60):
        super().__init__(daemon=True)
        self.manager = manager
        self.duration = duration

    def run(self):
        self.manager.in_retro_mode = True
        time.sleep(1.2)
        os.system("cls")

        term = RetroTerminal(duration=self.duration, manager=self.manager)
        term.run()

        os.system("cls")
        print("=== MCNP Auto Manage System ===")
        print("Code Name & Version = mcnp6, 6.3.0, production")
        print("Copyright Triad National Security, LLC/LANL/DOE - see LICENSE file\n")
        print("""\
    _/      _/        _/_/_/       _/      _/       _/_/_/         _/_/_/
    _/_/  _/_/      _/             _/_/    _/       _/    _/     _/
    _/  _/  _/      _/             _/  _/  _/       _/_/_/       _/_/_/
    _/      _/      _/             _/    _/_/       _/           _/    _/
    _/      _/        _/_/_/       _/      _/       _/             _/_/
    """)
        print(" ")
        print(f" mcnp6 ver=6.3.0,back time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Source version = release/6.3-55762725c4\n")
        self.manager.in_retro_mode = False
        self.manager._stable_since = None  # 重置穩定計時
        self.manager.release_retro_lock()
        
class RetroTerminal:
    def __init__(self, duration=60, manager=None):
        self.duration = duration
        self.manager = manager
        self.width = 60
        self.height = 10
        self.start_time = 0
        self.is_running = True

    def _clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    # --- 1. BIOS 啟動序列 ---
    def bios_boot(self):
        self._clear()
        print("\033[97m") 
        lines = [
            "AMIBIOS (C)1985 American Megatrends, Inc.",
            "MCNP-630 Processor Rev 2.0.26 Found",
            "Memory Test : 640KB OK",
            "Detecting HDD... [Fixed Disk: C]",
            "Loading MCNP-DOS Kernel...",
            ".........................."
        ]
        for line in lines:
            print(line)
            time.sleep(0.3)
        time.sleep(0.5)

    # --- 2. 數位雨特效 ---
    def matrix_rain(self, count=5, duration=1):
        chars = ["0", "1", " ", " ", "X", "Y", "Z", "!", "#", "*"]
        for _ in range(count):
            end = time.time() + duration
            while time.time() < end:
                line = "".join(random.choice(chars) for _ in range(70))
                sys.stdout.write(f"\r \033[92m{line}\033[0m")
                sys.stdout.flush()
                time.sleep(0.05)
            print("\033[0m")
        time.sleep(0.5)

    # --- 3. 星空螢幕保護程式 ---
    def starfield(self):
        stars = [[random.randint(0, self.width-1), random.randint(0, self.height-1)] for _ in range(25)]
        self._clear()
        print("\033[94m[ IDLE MODE - PRESS ANY KEY TO RETURN ]\033[0m\n")
        
        while not msvcrt.kbhit():
            screen = [[" " for _ in range(self.width)] for _ in range(self.height)]
            for s in stars:
                screen[s[1]][s[0]] = "."
                s[0] -= 1
                if s[0] < 0:
                    s[0] = self.width - 1
                    s[1] = random.randint(0, self.height - 1)
            
            output = "\n".join(["".join(row) for row in screen])
            # \033[3;1H 定位到第 3 行開始重繪
            sys.stdout.write("\033[3;1H" + "\033[94m" + output + "\033[0m")
            sys.stdout.flush()
            time.sleep(0.1)
        
        msvcrt.getch() # 消耗按鍵
        self._clear()
        print("MCNP-DOS Version 1.1 (C)1985 Quantum Dynamics")
        print("System awakened from idle mode.(Type 'HELP' for commands)\n")

    # --- 4. SHMUP 遊戲邏輯 ---
    def play_game(self):
        w, h = 40, 10
        ship_y = h // 2
        bullets, enemies = [], []
        score = 0
        self._clear()
        print("--- SHOT 'EM UP V1.1 ---")
        print("W/S: 移動, Space: 射擊, Q: 退出\n")
        
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch().lower()
                if key == b'w' and ship_y > 0: ship_y -= 1
                elif key == b's' and ship_y < h-1: ship_y += 1
                elif key == b' ': bullets.append([2, ship_y])
                elif key == b'q': break

            if random.random() < 0.25: enemies.append([w-1, random.randint(0, h-1)])
            
            # 移動與碰撞
            for b in bullets: b[0] += 2
            for e in enemies: e[0] -= 1
            
            new_bullets = []
            for b in bullets:
                hit = False
                for e in enemies[:]:
                    if b[1] == e[1] and (b[0] >= e[0] and b[0] <= e[0] + 1):
                        enemies.remove(e); hit = True; score += 10; break
                if not hit and b[0] < w: new_bullets.append(b)
            bullets = new_bullets

            for e in enemies:
                if e[1] == ship_y and e[0] <= 1:
                    print(f"\n!!! CRASHED !!! SCORE: {score}"); time.sleep(1.5); return
            
            enemies = [e for e in enemies if e[0] > 0]

            # 繪製畫面
            grid = [[" " for _ in range(w)] for _ in range(h)]
            grid[ship_y][1] = "}"
            for b in bullets: grid[b[1]][min(b[0], w-1)] = "-"
            for e in enemies: grid[e[1]][min(e[0], w-1)] = "<"
            
            output = f"SCORE: {score}  [W/S/SPACE/Q]\n+" + "-"*w + "+\n"
            output += "\n".join(["|" + "".join(row) + "|" for row in grid])
            output += "\n+" + "-"*w + "+"
            sys.stdout.write("\033[3;1H" + output)
            sys.stdout.flush()
            time.sleep(0.06)

    # --- 5. 指令處理器 ---
    def handle_command(self, cmd):
        if cmd == "HELP":
            print("Available commands: DIR, GAME, STATUS, CLS, HELP, EXIT")
        elif cmd == "DIR":
            print("\n Volume in drive C is MCNP_DATA")
            print(" Directory of C:\\\n")
            print("MCNP6    EXE    1,240,122  05-12-85")
            print("SHMUP    COM       45,102  01-10-86")
            print("      2 File(s)    1,285,224 bytes")
            print("\nPress any key to continue...")
            msvcrt.getch()
            print("")
        elif cmd == "GAME":
            self.play_game()
            self._clear()
            print("MCNP-DOS Version 1.1 (C)1985 Quantum Dynamics\n")
        elif cmd == "STATUS":
            if self.manager:
                print("\n" + self.manager.get_status_text())
            else:
                print("No manager attached.")
        elif cmd == "CLS":
            self._clear()
            print("MCNP-DOS Version 1.1 (C)1985 Quantum Dynamics\n")
        elif cmd == "EXIT":
            self.is_running = False
        elif cmd == "":
            pass
        else:
            print(f"Bad command or file name: '{cmd}'")

    # --- 6. 主執行入口 ---
    def run(self):
        self.bios_boot()
        self.matrix_rain()
        self._clear()
        print("MCNP-DOS Version 1.1 (C)1985 Quantum Dynamics")
        print("Waiting for resources... (Type 'HELP' for commands)\n")
        
        self.start_time = time.time()
        while self.is_running and (time.time() - self.start_time < self.duration):
            sys.stdout.write("C:\\> ")
            sys.stdout.flush()
            
            # 5秒待機偵測
            wait_start = time.time()
            has_input = False
            while time.time() - wait_start < 5:
                if msvcrt.kbhit():
                    has_input = True
                    break
                time.sleep(0.1)
            
            if has_input:
                cmd = input().upper().strip()
                self.handle_command(cmd)
            else:
                self.starfield()
        
class MCNPWorker(threading.Thread):
    def __init__(self, task_id, input_file, batch_path, model_dir, on_finish_callback, on_spawn_callback):
        super().__init__()
        self.task_id = task_id
        self.input_path = Path(input_file)
        self.model_dir = Path(model_dir)
        self.batch_path = batch_path
        self.on_finish = on_finish_callback
        self.on_spawn = on_spawn_callback

        self.input_name = self.input_path.name
        self.original_dir = self.input_path.parent

    def safe_move(self, src, dst):
        if not src.exists():
            return

        # 如果來源與目的地是同一路徑 → 不動
        if src.resolve() == dst.resolve():
            return

        try:
            if dst.exists():
                dst.unlink()
            shutil.move(str(src), str(dst))
        except Exception as e:
            print(f"[MOVE ERROR] {src} -> {dst} : {e}")

    def run(self):
        try:
            target_input = self.model_dir / self.input_name
            self.safe_move(self.input_path, target_input)

            # print(f"run {self.input_name}")

            base = self.input_path.stem
            output_name = f"{base}.o"

            cmd = (
                f'cmd /c "call \"{self.batch_path}\" '
                f'&& mcnp6 i=\"{self.input_name}\" o=\"{output_name}\""'
            )
            # print(cmd)

            process = subprocess.Popen(
                cmd,
                cwd=str(self.model_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.on_spawn(self.task_id, process.pid)
            process.wait()

        except Exception as e:
            print(f"[WORKER ERROR] {self.input_name}: {e}")

        finally:
            # 不論成功失敗都嘗試搬回
            base = self.input_path.stem

            for ext in [".o", ".r", ".m", ".log", ".mctal", self.input_path.suffix]:
                src_file = self.model_dir / (base + ext)
                dst_file = self.original_dir / (base + ext)
                self.safe_move(src_file, dst_file)

            # 一定要回報完成
            self.on_finish(self.task_id)
        
class MCNPManager:
    def __init__(self, batch_path, model_dir, input_files, monitor_instance):
        self.batch_path = batch_path
        self.model_dir = model_dir
        self.monitor = monitor_instance
        
        self.in_retro_mode = False
        self._retro_lock = threading.Lock()
        self._last_state = None
        self._stable_since = None

        # 用 uuid 包裝每個任務
        self.pending = [
            (uuid.uuid4(), file_path)
            for file_path in input_files
        ]

        self.running = {}   # {task_id: file_path}
        self.finished = {}  # {task_id: file_path}

        self.lock = threading.Lock()
        
    def is_stable_for(self, seconds):
        with self.lock:
            current_state = (
                len(self.running),
                len(self.pending),
                len(self.finished)
            )

            now = time.time()

            if self._last_state != current_state:
                self._last_state = current_state
                self._stable_since = now
                return False

            if self._stable_since is None:
                self._stable_since = now
                return False

            return (now - self._stable_since) > seconds

    def on_task_done(self, task_id):
        """當 Worker 跑完時會呼叫這個函數"""
        with self.lock:
            if task_id in self.running:
                pid = self.running[task_id].get("pid")
                if pid:
                    self.monitor.remove_pid(pid)

                task_info = self.running.pop(task_id)
                self.finished[task_id] = task_info["path"]
                
    def on_spawn(self, task_id, pid):
        with self.lock:
            self.running[task_id]["pid"] = pid
        self.monitor.add_pid(pid)

    def update_loop(self):
        """這是在背景跑的迴圈"""
        while self.pending or self.running:
            # 1. 檢查 Monitor 資源是否 OK
            if self.pending and self.monitor.is_system_okay():
                with self.lock:
                    task_id, file_to_run = self.pending.pop(0)

                    self.running[task_id] = {
                        "path": file_to_run,
                        "start_time": time.time()
                    }

                    worker = MCNPWorker(
                        task_id,
                        file_to_run,
                        self.batch_path,
                        self.model_dir,
                        self.on_task_done,
                        self.on_spawn
                    )
                    self.monitor.last_start_time = time.time()
                    worker.start()
            
            # 2. 這裡你可以把實時訊息印出來
            if not self.in_retro_mode:
                self.display_status()
                
            time.sleep(1)
    
    def get_status_text(self):
        """
        取得任務狀態
        """
        now = time.time()

        with self.lock:
            running_names = [
                f"{os.path.basename(info['path'])} "
                f"({int(now - info['start_time'])//3600:02d}:"
                f"{int(now - info['start_time'])%3600//60:02d}:"
                f"{int(now - info['start_time'])%60:02d})"
                for info in self.running.values()
            ]

            pending_count = len(self.pending)
            finished_count = len(self.finished)
            running_count = len(self.running)

        return (
            f"[狀態]\n"
            f"待處理: {pending_count}\n"
            f"執行中: {running_count}\n"
            f"已完成: {finished_count}\n\n"
            f"[執行中任務]\n"
            f"{', '.join(running_names) if running_names else 'IDLE'}"
        )
        
    def _get_spinner(self, t):
        # 建立一個左右來回移動的符號，表示正在運算
        icons = ["■----", "-■---", "--■--", "---■-", "----■", "---■-", "--■--", "-■---"]
        return icons[int(t * 4) % len(icons)]
        
    def display_status(self):
        """
        顯示任務狀態
        """
        now = time.time()
        with self.lock:
            running_names = [
                f"{os.path.basename(info['path'])} "
                f"({int(now - info['start_time'])//3600:02d}:" 
                f"{int(now - info['start_time'])% 3600//60:02d}:"
                f"{int(now - info['start_time'])%60:02d})"
                for info in self.running.values()
            ]

            pending_count = len(self.pending)
            finished_count = len(self.finished)
            running_count = len(self.running)

        try:
            columns, lines = os.get_terminal_size()
        except OSError:
            columns, lines = 80, 30

        start_line = max(1, lines - 6)

        status_output = (
            f"\033[{start_line};1H" + "\033[K" + "="*columns + "\n" +
            f"\033[K [狀態] 待處理: {pending_count:2d} | "
            f"執行中: {running_count:2d} | "
            f"已完成: {finished_count:2d}\n" +
            f"\033[K [執行] {', '.join(running_names) if running_names else 'IDLE'} {self._get_spinner(time.time())}\n" +
            f"\033[K [隊列] 還有 {pending_count} 個任務排隊中...\n" +
            f"\033[K" + "="*columns
        )

        sys.stdout.write(status_output)
        sys.stdout.flush()
        
    def release_retro_lock(self):
        if self._retro_lock.locked():
            self._retro_lock.release()
    
def main():
    if os.name == 'nt': ctypes.windll.kernel32.SetConsoleTitleW("MCNP 6.3.0 Command Windaw")
    # 1. 確保 Windows CMD 支援 ANSI 轉義碼 (顏色與定位)
    if os.name == 'nt': os.system('')

    # 2. 初始化顯示介面
    # os.system('cls')
    print("          === MCNP Auto Manage System ===")
    print("          Code Name & Version = mcnp6, 6.3.0, production")
    print("          Copyright Triad National Security, LLC/LANL/DOE - see LICENSE file\n")
    print("""\
     _/      _/        _/_/_/       _/      _/       _/_/_/         _/_/_/
    _/_/  _/_/      _/             _/_/    _/       _/    _/     _/
   _/  _/  _/      _/             _/  _/  _/       _/_/_/       _/_/_/
  _/      _/      _/             _/    _/_/       _/           _/    _/
 _/      _/        _/_/_/       _/      _/       _/             _/_/
""")
    print(" ")
    print(f" mcnp6 ver=6.3.0,start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Source version = release/6.3-55762725c4\n")
    
    # 3. 獲取執行參數
    
    loader = ConfigLoader()
    ''''''
    batch_pth = loader.select_file(title="選擇 MCNP 環境批次檔", default_file="mcnp_630_env.bat")
    if not batch_pth: exit("沒有選擇 batch 檔")
    else: print(f"'{batch_pth}' had been selected.")
    model_pth = loader.select_folder(title="選擇含有模型參數的資料夾 (Model Dir)")
    if not model_pth: exit("沒有選擇目標資料夾")
    else: print(f"It will process in folder '{model_pth}'")
    input_files = loader.select_input_files(title="選擇模型輸入檔 (xxx.i)")
    if not input_files: exit("沒有選擇檔案")
    else: print(f"selected '{len(input_files)}' files.")
    num1, num2 = loader.select_two_numbers()
    
    loader.close()
    # 4. 建立任務
    monitor = ResourceMonitor(cpu_limit=num1, ram_limit=num2, cooldown=5)
    monitor.start()
    
    manager = MCNPManager(batch_pth, model_pth, input_files, monitor)
    manager_thread = threading.Thread(target=manager.update_loop, daemon=True)
    manager_thread.start()
    # 監控穩定狀態
    while manager_thread.is_alive():

        if manager.is_stable_for(20):
            if manager._retro_lock.acquire(blocking=False):
                retro = RetroRunner(manager, duration=120)
                retro.start()

        time.sleep(2)
    
if __name__ == "__main__":
    main()
